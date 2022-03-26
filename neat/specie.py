from __future__ import annotations

from copy import deepcopy
import math
import random

import neat
from .genome import Genome
from mattslib.dict import countOccurrence, sortIntoDict
from mattslib.math_util import mean

__version__ = '1.4.3'
__date__ = '26/03/2022'


def genomicDistance(x_member: Genome, y_member: Genome, distance_weights: dict) -> float:
    """
    Calculates the distance between genomes by summing the distance between the corresponding genes.
    :param x_member: Genome
    :param y_member: Genome
    :param distance_weights: dict[str: int | float]
    :return:
        - distance - float
    """
    genomic_distance = 0
    x_connections = list(x_member.connections)
    y_connections = list(y_member.connections)
    connections = countOccurrence(x_connections + y_connections)

    matching_connections = [pos for pos in connections if connections[pos] >= 2]
    disjoint_connections = [pos for pos in connections if connections[pos] == 1]

    connections_count = len(max(x_connections, y_connections))
    nodes_count = min(x_member.total_nodes, y_member.total_nodes)

    genomic_distance += distance_weights['node'] * (abs(x_member.total_nodes - y_member.total_nodes) /
                                                    max(x_member.total_nodes, y_member.total_nodes))
    genomic_distance += distance_weights['connection'] * (len(disjoint_connections) / connections_count)

    weight_diff = 0
    for pos in matching_connections:
        weight_diff += abs(x_member.connections[pos].weight - y_member.connections[pos].weight)

    genomic_distance += distance_weights['weight'] * (weight_diff / len(matching_connections))

    activation_diff, bias_diff = 0, 0
    for node in range(nodes_count):
        activation_diff += 1 if x_member.nodes[node].activation != y_member.nodes[node].activation else 0
        bias_diff += abs(x_member.nodes[node].bias - y_member.nodes[node].bias)

    genomic_distance += distance_weights['activation'] * (activation_diff / nodes_count)
    genomic_distance += distance_weights['bias'] * (bias_diff / nodes_count)
    return genomic_distance


class Specie(object):
    """
    Separates the population into species with similar genomic distance.
    """
    def __init__(self, settings: Settings, member: Genome, distance: float = 0):
        """
        Initiates the Specie object with given values.
        :param settings: Settings
        :param member: Genome
        :param distance: float
        """
        self.settings = settings
        self.members = [member]
        self.distances = [distance]
        self.representative = 0
        self.fitness_history = []
        self.fitness_mean = 0

    def updateFitness(self) -> None:
        """
        Adjusts the fitness for the members and update the specie fitness.
        :return:
            - None
        """
        for member in self.members:
            member.adjusted_fitness = member.fitness / len(self.members)

        self.fitness_mean = int(round(mean(self.getAllFitnesses())))
        self.fitness_history.append(self.fitness_mean)

        if len(self.fitness_history) > self.settings.max_fitness_history:
            self.fitness_history.pop(0)

    def killGenomes(self, remove_duplicate: bool, elitism: bool = False) -> None:
        """
        Kills duplicate genomes and a portion of inferior genomes.
        :param remove_duplicate: bool
        :param elitism: bool
        :return:
            - None
        """
        max_survive = int(math.ceil((1 - self.settings.kill) * len(self.members))) if not elitism else 1

        if remove_duplicate:
            self.removeDuplicate()

        ids = [i for i in range(len(self.members))]
        sorted_ids = sortIntoDict(ids, sort_with=self.getAllFitnesses())

        sorted_fitness_keys = sorted(list(sorted_ids.keys()), reverse=True)
        surviving_members, surviving_distances = [], []
        for fitness_key in sorted_fitness_keys:
            for member_id in sorted_ids[fitness_key]:
                if len(surviving_members) < max_survive:
                    surviving_members.append(self.members[member_id])
                    surviving_distances.append(self.distances[member_id])
                else:
                    break
        self.representative = 0
        self.members = surviving_members
        self.distances = surviving_distances

    def removeDuplicate(self):
        ids = [i for i in range(len(self.members))]
        sorted_ids = sortIntoDict(ids, sort_with=self.distances)
        sorted_distance_keys = sorted(list(sorted_ids.keys()))

        duplicate_genomes = []
        # for distance in sorted_distance_keys:
        #     if distance != 0:
        #         for genome_a in range(len(sorted_ids[distance]) - 1):
        #             member_id = sorted_ids[distance][genome_a]
        #             for genome_b in range(genome_a + 1, len(sorted_ids[distance])):
        #                 if member_id not in duplicate_genomes:
        #                     duplicate_distance = genomicDistance(self.members[member_id],
        #                                                          self.members[sorted_ids[distance][genome_b]],
        #                                                          self.settings.distance_weights)
        #                     if duplicate_distance <= self.settings.delta_duplicate_threshold:
        #                         print(f"Duplicate_With_Same_Distance: {distance}, {duplicate_distance}")
        #                         duplicate_genomes.append(member_id)
        for i in range(1, len(sorted_distance_keys)):
            distance_a = sorted_distance_keys[i]
            distance_b = sorted_distance_keys[i - 1]
            if distance_a != 0 and distance_b != 0:
                if abs(distance_a - distance_b) <= self.settings.delta_duplicate_threshold:
                    duplicate_distance = genomicDistance(self.members[sorted_ids[distance_a][0]],
                                                         self.members[sorted_ids[distance_b][0]],
                                                         self.settings.distance_weights)
                    if duplicate_distance <= self.settings.delta_duplicate_threshold:
                        for member_id in sorted_ids[distance_b]:
                            if member_id not in duplicate_genomes:
                                print(f"Duplicate_With_Different_Distance: {distance_a} - {distance_b}",
                                      duplicate_distance)
                                duplicate_genomes.append(member_id)

        if duplicate_genomes:
            temp_members = []
            temp_distances = []
            for i in range(len(self.members)):
                if i not in duplicate_genomes:
                    temp_members.append(self.members[i])
                    temp_distances.append(self.distances[i])
            self.members = temp_members
            self.distances = temp_distances

    def updateRepresentative(self) -> None:
        """
        Searches through members in specie for leading genome with the highest
        fitness to be the representative.
        :return:
            - None
        """
        temp_representative = self.representative
        for i, member in enumerate(self.members):
            if member.fitness > self.members[self.representative].fitness:
                self.representative = i
        self.distances[temp_representative] = genomicDistance(self.members[temp_representative],
                                                              self.members[self.representative],
                                                              self.settings.distance_weights)
        self.distances[self.representative] = 0

    def shouldSurvive(self) -> bool:
        """
        Checks the fitness against settings to permit survival.
        :return:
            - survive - bool
        """
        if len(self.fitness_history) < self.settings.max_fitness_history:
            return True
        if mean(self.fitness_history) > self.fitness_history[0]:
            return True
        return False

    def getAllFitnesses(self) -> list:
        """
        Gets the fitness of each member in specie.
        :return:
            - fitnesses - list[int | float]
        """
        return [member.fitness for member in self.members]
