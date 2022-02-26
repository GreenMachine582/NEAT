import random
import copy
import math
from neat.genome import Genome


def genomic_crossover(a, b):
    child = Genome(a.inputs, a.outputs, a.default_activation)
    a_in = set(a.connections)
    b_in = set(b.connections)

    for i in a_in & b_in:
        parent = random.choice([a, b])
        child.connections[i] = copy.deepcopy(parent.connections[i])

    if a.fitness > b.fitness:
        for i in a_in - b_in:
            child.connections[i] = copy.deepcopy(a.connections[i])
    else:
        for i in b_in - a_in:
            child.connections[i] = copy.deepcopy(b.connections[i])

    child._max_node = 0
    for (i, j) in child.connections:
        current_max = max(i, j)
        child._max_node = max(child.total_nodes, current_max)
    child.total_nodes += 1

    for n in range(child.total_nodes):
        inherit_from = []
        if n in a.nodes:
            inherit_from.append(a)
        if n in b.nodes:
            inherit_from.append(b)

        random.shuffle(inherit_from)
        parent = max(inherit_from, key=lambda p: p.fitness)
        child.nodes[n] = copy.deepcopy(parent.nodes[n])

    child.reset()
    return child


class Specie(object):
    def __init__(self, max_fitness_history, *members):
        self.members = list(members)
        self.fitness_history = []
        self.fitness_sum = 0
        self.max_fitness_history = max_fitness_history

    def breed(self, mutation_probabilities, breed_probabilities):
        population = list(breed_probabilities.keys())
        probabilities = [breed_probabilities[k] for k in population]
        choice = random.choices(population, weights=probabilities)[0]

        child = None
        if choice == "asexual" or len(self.members) == 1:
            child = random.choice(self.members).clone()
            child.mutate(mutation_probabilities)
        elif choice == "sexual":
            (mom, dad) = random.sample(self.members, 2)
            child = genomic_crossover(mom, dad)

        return child

    def update_fitness(self):
        """Update the adjusted fitness values of each genome
        and the historical fitness."""
        for g in self.members:
            g._adjusted_fitness = g.fitness / len(self.members)

        self.fitness_sum = sum([g._adjusted_fitness for g in self.members])
        self.fitness_history.append(self.fitness_sum)
        if len(self.fitness_history) > self.max_fitness_history:
            self.fitness_history.pop(0)

    def cull_genomes(self, fittest_only):
        self.members.sort(key=lambda g: g.fitness, reverse=True)
        if fittest_only:
            remaining = 1
        else:
            remaining = int(math.ceil(0.25 * len(self.members)))

        self.members = self.members[:remaining]

    def get_best(self):
        return max(self.members, key=lambda g: g.fitness)

    def can_progress(self):
        n = len(self.fitness_history)
        avg = sum(self.fitness_history) / n
        return avg > self.fitness_history[0] or n < self.max_fitness_history
