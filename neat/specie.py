from __future__ import annotations

from copy import deepcopy
import math
import random

from .genome import Genome
from mattslib.dict import countOccurrence, sortIntoDict
from mattslib.math_util import mean

__version__ = '1.4.1'
__date__ = '22/03/2022'


class Specie(object):
    """
    Separates the population into species with similar genomic distance.
    """
    def __init__(self, max_fitness_history: int, members: list = None):
        """
        Initiates the Specie object with given values.
        :param max_fitness_history: int
        :param members: list
        """
        self.members = [] if members is None else members
        self.representative = None
        self.fitness_history = []
        self.fitness_mean = 0
        self.max_fitness_history = max_fitness_history

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
        sorted_genomes = sortIntoDict(self.members, sort_with=self.getAllFitnesses())
        sorted_genomes = sum(sorted_genomes.values(), [])

        survived = int(math.ceil((1 - kill) * len(self.members))) if not elitism else 1
        sorted_genomes = sorted_genomes[::-1]
        self.members = sorted_genomes[:survived]

    def getRepresentative(self) -> None:
        """
        Searches through members in specie for leading representative
        fitness.
        :return:
            - None
        """
        representative = self.members[0]
        for member in self.members:
            if member.fitness > representative.fitness:
                representative = member
        self.representative = representative
        return representative

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
