from __future__ import annotations

from copy import deepcopy
import math
import random

import neat
from .genome import Genome
from mattslib.dict import countOccurrence, sortIntoDict
from mattslib.math_util import mean

__version__ = '1.4.4'
__date__ = '28/03/2022'


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
    return round(genomic_distance, 7)


class Specie(object):
    """
    Separates the population into species with similar genomic distance.
    """
    def __init__(self, settings: Settings, member: Genome):
        """
        Initiates the Specie object with given values.
        :param settings: Settings
        :param member: Genome
        """
        self.settings = settings
        self.members = [member]
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
            distances = self.getDistances()
            duplicate_genomes = []

            for genome_key, distance in enumerate(distances):
                if genome_key != self.representative and distance <= self.settings.duplicate_distance_threshold:
                    duplicate_genomes.append(genome_key)

            duplicate_genomes = duplicate_genomes[::-1]
            for genome_key in duplicate_genomes:
                self.members.pop(genome_key)

        ids = [i for i in range(len(self.members))]
        sorted_ids = sortIntoDict(ids, sort_with=self.getAllFitnesses())

        sorted_fitness_keys = sorted(list(sorted_ids.keys()), reverse=True)
        surviving_members, surviving_distances = [], []
        for fitness_key in sorted_fitness_keys:
            for member_id in sorted_ids[fitness_key]:
                if len(surviving_members) < max_survive:
                    surviving_members.append(self.members[member_id])
                else:
                    break
        self.members = surviving_members

    def updateRepresentative(self) -> None:
        """
        Searches through members in specie for leading genome with the highest
        fitness to be the representative.
        :return:
            - None
        """
        for i, member in enumerate(self.members):
            if member.fitness > self.members[self.representative].fitness:
                self.representative = i

    def getDistances(self) -> list:
        """
        Gets the genomic distance for each member in respects to the representative.
        :return:
            - distances - list[int | float]
        """
        distances = []
        for member_key, member in enumerate(self.members):
            distance = 0
            if member_key != self.representative:
                distance = genomicDistance(member, self.members[self.representative], self.settings.distance_weights)
            distances.append(distance)
        return distances

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
