from __future__ import annotations

from copy import deepcopy
import math
import random

import neat
from .genome import Genome
from mattslib.dict import countOccurrence, sortIntoDict
from mattslib.math_util import mean, euclideanDistance, brayCurtisIndividualDistance

__version__ = '1.4.10'
__date__ = '24/04/2022'


def genomicDistance(x_member: Genome, y_member: Genome, distance_weights: dict) -> float:
    """
    Calculates an estimated distance between two genomes using the Euclidean distance formular.
    :param x_member: Genome
    :param y_member: Genome
    :param distance_weights: dict[str: float]
    :return:
        - distance - float
    """
    genomic_distance = 0.0

    genomic_distance += distance_weights['node'] * euclideanDistance(x_member.total_nodes, y_member.total_nodes)
    genomic_distance += distance_weights['connection'] * euclideanDistance(x_member.total_connections,
                                                                           y_member.total_connections)

    counts = countOccurrence(list(x_member.connections) + list(y_member.connections))
    matching_connections = [pos for pos in counts if counts[pos] == 2]
    x_weight = [x_member.connections[pos].weight for pos in x_member.connections if pos in matching_connections]
    y_weight = [y_member.connections[pos].weight for pos in y_member.connections if pos in matching_connections]
    genomic_distance += distance_weights['weight'] * brayCurtisIndividualDistance(x_weight, y_weight)

    x_bias = [x_member.nodes[node_key].bias for node_key in x_member.nodes]
    y_bias = [y_member.nodes[node_key].bias for node_key in y_member.nodes]
    genomic_distance += distance_weights['bias'] * brayCurtisIndividualDistance(sorted(x_bias), sorted(y_bias))
    return round(genomic_distance, 7)


class Specie(object):
    """
    Divides the population into manageable species based on the calculated genomic distance.
    """
    def __init__(self, settings: Settings, member: Genome):
        """
        Initiates the Specie object with given values.
        :param settings: Settings
        :param member: Genome
        """
        self.settings = settings
        self.members = [member]
        self.representative = member
        self.fitness_history = []
        self.fitness_mean = 0

    def updateFitness(self) -> None:
        """
        Adjusts each member's fitness and calculates the species
        mean fitness.
        :return:
            - None
        """
        for member in self.members:
            member.adjusted_fitness = member.fitness / len(self.members)

        self.fitness_mean = int(round(mean(self.getAllFitnesses())))

    def updateFitnessHistory(self) -> None:
        """
        Updates the fitness history with mean fitness.
        :return:
            - None
        """
        self.fitness_history.append(self.fitness_mean)
        if len(self.fitness_history) > self.settings.max_fitness_history:
            self.fitness_history.pop(0)

    def killGenomes(self, remove_duplicate: bool = False, elitism: bool = False) -> None:
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
                if self.members[genome_key] != self.representative:
                    if distance <= self.settings.duplicate_distance_threshold:
                        duplicate_genomes.append(genome_key)

            duplicate_genomes = duplicate_genomes[::-1]
            for genome_key in duplicate_genomes:
                self.members.pop(genome_key)

        ids = [member_key for member_key in range(len(self.members))]
        sorted_ids = sortIntoDict(ids, sort_with=self.getAllFitnesses())

        sorted_fitness_keys = sorted(list(sorted_ids))
        surviving_members = []
        for fitness_key in sorted_fitness_keys:
            for member_id in sorted_ids[fitness_key]:
                if len(surviving_members) < max_survive:
                    surviving_members.append(self.members[member_id])
                else:
                    break
        self.members = surviving_members

    def updateRepresentative(self) -> None:
        """
        The species representative is an assigned member with the highest adjusted fitness.
        :return:
            - None
        """
        self.representative = self.members[0]
        for member in self.members:
            if member.adjusted_fitness > self.representative.adjusted_fitness:
                self.representative = member

    def getDistances(self) -> list:
        """
        Gets the genomic distance for each member in respects to the representative.
        :return:
            - distances - list[float]
        """
        distances = []
        for member in self.members:
            distance = 0
            if member != self.representative:
                distance = genomicDistance(member, self.representative, self.settings.distance_weights)
            distances.append(distance)
        return distances

    def shouldSurvive(self) -> bool:
        """
        Checks if the specie meets the minimum requirements to survive.
        :return:
            - survive - bool
        """
        if len(self.fitness_history) <= self.settings.max_fitness_history:
            return True
        if mean(self.fitness_history) > self.fitness_history[0]:
            return True
        return False

    def getAllFitnesses(self) -> list:
        """
        Gets the adjusted fitness of each member in specie.
        :return:
            - fitnesses - list[int | float]
        """
        return [member.adjusted_fitness for member in self.members]
