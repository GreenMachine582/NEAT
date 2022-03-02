import math
import random
from copy import deepcopy

from neat.genome import Genome
from mattslib.list import mean, countOccurrence, sortIntoDict

__file__ = 'specie'
__version__ = '1.2'
__date__ = '02/03/2022'


def genomic_crossover(x_member, y_member):
    child = Genome(x_member.inputs, x_member.outputs, x_member.activation)

    x_connections = list(x_member.connections)
    y_connections = list(y_member.connections)
    connections = countOccurrence(x_connections + y_connections)

    matching_connections = [i for i in connections if connections[i] == 2]
    disjoint_connections = [i for i in connections if connections[i] == 1]

    for pos in matching_connections:
        parent = random.choice([x_member, y_member])
        child.connections[pos] = deepcopy(parent.connections[pos])

    if x_member.fitness > y_member.fitness:
        for pos in x_connections:
            if pos in disjoint_connections:
                child.connections[pos] = deepcopy(x_member.connections[pos])
    else:
        for pos in y_connections:
            if pos in disjoint_connections:
                child.connections[pos] = deepcopy(y_member.connections[pos])

    child.total_nodes = 0
    for pos in child.connections:
        current_max = max(pos[0], pos[1])
        child.total_nodes = max(child.total_nodes, current_max)
    child.total_nodes += 1

    for node in range(child.total_nodes):
        inherit_from = []
        if node in x_member.nodes:
            inherit_from.append(x_member)
        if node in y_member.nodes:
            inherit_from.append(y_member)

        random.shuffle(inherit_from)
        parent, fitness = inherit_from[0], inherit_from[0].fitness
        for member in inherit_from:
            if member.fitness > fitness:
                parent, fitness = member, member.fitness
        child.nodes[node] = deepcopy(parent.nodes[node])

    child.reset()
    return child


class Specie(object):
    def __init__(self, max_fitness_history, *members):
        self.members = list(members)
        self.fitness_history = []
        self.fitness_mean = 0
        self.max_fitness_history = max_fitness_history

    def breed(self, mutation_probabilities, breed_probabilities):
        population = list(breed_probabilities.keys())
        probability_weights = [breed_probabilities[mutation] for mutation in population]
        mutation = random.choices(population, weights=probability_weights)[0]

        child = None
        if mutation == "asexual" or len(self.members) == 1:
            child = deepcopy(random.choice(self.members))
            child.mutate(mutation_probabilities)
        elif mutation == "sexual":
            (x_member, y_member) = random.sample(self.members, 2)
            child = genomic_crossover(x_member, y_member)
        return child

    def updateFitness(self):
        for member in self.members:
            member.adjusted_fitness = member.fitness / len(self.members)

        self.fitness_mean = mean(self.getAllFitnesses())
        self.fitness_history.append(self.fitness_mean)

        if len(self.fitness_history) > self.max_fitness_history:
            self.fitness_history.pop(0)

    def killGenomes(self, preserve=0.25, elitism=False):
        fitnesses = [genome.fitness for genome in self.members]
        sorted_genomes = sortIntoDict(self.members, sort_with=fitnesses)
        sorted_genomes = sum(sorted_genomes.values(), [])

        survived = int(math.ceil(preserve * len(self.members))) if not elitism else 1
        sorted_genomes = sorted_genomes[::-1]
        self.members = sorted_genomes[:survived]

    def getBest(self):
        best_genome = self.members[0]
        for member in self.members:
            if member.fitness > best_genome.fitness:
                best_genome = member
        return best_genome

    def canProgress(self):
        if len(self.fitness_history) < self.max_fitness_history or mean(self.fitness_history) > self.fitness_history[0]:
            return True
        return False

    def getAllFitnesses(self):
        return [member.fitness for member in self.members]
