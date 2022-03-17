from __future__ import annotations

from copy import deepcopy
import math
import random

from .genome import Genome
from mattslib.dict import countOccurrence, sortIntoDict
from mattslib.list import mean

__version__ = '1.4'
__date__ = '18/03/2022'


class Specie(object):
    def __init__(self, max_fitness_history, *members):
        # update
        self.members = list(members)
        self.fitness_history = []
        self.fitness_mean = 0
        self.max_fitness_history = max_fitness_history

    def updateFitness(self) -> None:
        # update
        for member in self.members:
            member.adjusted_fitness = member.fitness / len(self.members)

        self.fitness_mean = mean(self.getAllFitnesses())
        self.fitness_history.append(self.fitness_mean)

        if len(self.fitness_history) > self.max_fitness_history:
            self.fitness_history.pop(0)

    def killGenomes(self, kill, elitism: bool = False) -> None:
        """
        Sorts the members by fitness then kills inferior genomes.
        :param kill: int | float
        :param elitism: bool
        :return:
            - None
        """
        sorted_genomes = sortIntoDict(self.members, sort_with=getAllFitnesses())
        sorted_genomes = sum(sorted_genomes.values(), [])

        survived = int(math.ceil((1 - kill) * len(self.members))) if not elitism else 1
        sorted_genomes = sorted_genomes[::-1]
        self.members = sorted_genomes[:survived]

    def getBest(self) -> Genome:
        """
        Searches through members in specie for member with highest
         fitness.
        :return:
            - best_genome - Genome
        """
        best_genome = self.members[0]
        for member in self.members:
            if member.fitness > best_genome.fitness:
                best_genome = member
        return best_genome

    def shouldSurvive(self) -> bool:
        """
        Checks the fitness against settings to permit survival.
        :return:
            - survive - bool
        """
        if len(self.fitness_history) < self.max_fitness_history or mean(self.fitness_history) > self.fitness_history[0]:
            return True
        return False

    def getAllFitnesses(self) -> list:
        """
        Gets the fitness of each member in specie.
        :return:
            - fitnesses - list[int | float]
        """
        return [member.fitness for member in self.members]
