from __future__ import annotations

from copy import deepcopy
import pickle
import random

from .genome import Genome
from .settings import Settings
from .specie import Specie
from mattslib.dict import countOccurrence

__version__ = '1.4.1'
__date__ = '17/03/2022'


def genomicDistance(x_member, y_member, distance_weights):
    x_connections = list(x_member.connections)
    y_connections = list(y_member.connections)
    connections = countOccurrence(x_connections + y_connections)

    matching_connections = [i for i in connections if connections[i] >= 2]
    disjoint_connections = [i for i in connections if connections[i] == 1]
    count_connections = len(max(x_connections, y_connections))
    count_nodes = min(x_member.total_nodes, y_member.total_nodes)

    weight_diff = 0
    for i in matching_connections:
        weight_diff += abs(x_member.connections[i].weight - y_member.connections[i].weight)

    bias_diff = 0
    for i in range(count_nodes):
        bias_diff += abs(x_member.nodes[i].bias - y_member.nodes[i].bias)

    t1 = distance_weights['connection'] * (len(disjoint_connections) / count_connections)
    t2 = distance_weights['weight'] * (weight_diff / len(matching_connections))
    t3 = distance_weights['bias'] * (bias_diff / count_nodes)
    return t1 + t2 + t3


def genomicCrossover(x_member, y_member):
    child = Genome(x_member.inputs, x_member.outputs, x_member.node_info)

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


class NEAT(object):

    def __init__(self, settings_dir=''):
        self.settings = Settings(settings_dir)
        self.inputs = 0
        self.outputs = 0

        self.species = []
        self.population = 0

        self.generation = 0
        self.current_species = 0
        self.current_genome = 0

        self.best_genome = None

    def generate(self, inputs, outputs, population=100):
        self.inputs = inputs
        self.outputs = outputs
        self.population = population

        for _ in range(self.population):
            genome = Genome(self.inputs, self.outputs, self.settings.node_info)
            self.classifyGenome(genome)

        self.best_genome = self.species[0].members[0]

    def classifyGenome(self, genome):
        if not self.species:
            self.species.append(Specie(self.settings.max_fitness_history, genome))
        else:
            for specie in self.species:
                representative_of_specie = specie.members[0]
                distance = genomicDistance(genome, representative_of_specie, self.settings.distance_weights)
                if distance <= self.settings.delta_genome_threshold:
                    specie.members.append(genome)
                    return
            self.species.append(Specie(self.settings.max_fitness_history, genome))

    def updateFitness(self):
        leading_genomes = [specie.getBest() for specie in self.species]
        best_genome = leading_genomes[0]
        for leading_genome in leading_genomes:
            if leading_genome.fitness > best_genome.fitness:
                best_genome = leading_genome
        self.best_genome = deepcopy(best_genome)

    def breed(self, probabilities, specie_key):
        crossover_by = random.choices(list(probabilities['crossover'].keys()),
                                      weights=list(probabilities['crossover'].values()))[0]
        breed_by = random.choices(list(probabilities['breed'].keys()),
                                  weights=list(probabilities['breed'].values()))[0]
        x_member, y_member = None, None
        if crossover_by == 'intraspecies' or breed_by == 'asexual':
            if breed_by == "asexual" or len(self.species[specie_key].members) == 1:
                child = deepcopy(random.choice(self.species[specie_key].members))
                child.mutate(self.settings.mutation_probabilities)
                return child
            elif breed_by == 'sexual':
                (x_member, y_member) = random.sample(self.species[specie_key].members, 2)
        elif crossover_by == 'interspecies':
            species = [i for i in range(len(self.species)) if i != specie_key]
            x_member = random.choice(self.species[specie_key].members)
            y_member = random.choice(self.species[random.choice(species)].members)
        return genomicCrossover(x_member, y_member)

    def killPopulation(self):
        surviving_species = []
        for specie in self.species:
            if specie.shouldSurvive():
                surviving_species.append(specie)
        self.species = surviving_species

        for specie in self.species:
            specie.killGenomes(self.settings.kill)

    def repopulate(self, fitness_sum):
        if self.species:
            for specie_key, specie in enumerate(self.species):
                offspring = int(round((specie.fitness_mean / fitness_sum) * (self.population - self.getPopulation())))
                for _ in range(offspring):
                    child = self.breed(self.settings.breed_probabilities, specie_key)
                    self.classifyGenome(child)
        else:
            for p in range(self.population):
                if p % 3 == 0:
                    genome = deepcopy(self.best_genome)
                else:
                    genome = Genome(self.inputs, self.outputs, self.settings.node_info)
                genome.mutate(self.settings.mutation_probabilities)
                self.classifyGenome(genome)

    def evolve(self):
        fitness_sum = 0
        for specie in self.species:
            specie.updateFitness()
            fitness_sum += specie.fitness_mean

        if fitness_sum == 0:
            for specie in self.species:
                for member in specie.members:
                    member.mutate(self.settings.mutation_probabilities)
        else:
            self.killPopulation()
            self.repopulate(fitness_sum)
        self.generation += 1

    def shouldEvolve(self):
        self.updateFitness()
        if self.settings.max_generations and self.generation >= self.settings.max_generations:
            if self.settings.max_fitness and self.best_genome.fitness >= self.settings.max_fitness:
                return False
        return True

    def nextGenome(self):
        specie = self.species[self.current_species]
        if self.current_genome < len(specie.members) - 1:
            self.current_genome += 1
        else:
            if self.current_species < len(self.species) - 1:
                self.current_species += 1
            else:
                self.evolve()
                self.current_species = 0
            self.current_genome = 0

    def getCurrent(self):
        return self.generation, self.best_genome.fitness

    def getGenome(self, specie=None, genome=None):
        specie = self.current_species if specie is None else specie
        genome = self.current_genome if genome is None else genome
        return self.species[specie].members[genome]

    def getPopulation(self):
        return sum([len(specie.members) for specie in self.species])

    def getInfo(self):
        neat_info = {'generation': self.generation+1, 'current_species': self.current_species+1,
                     'current_genome': self.current_genome+1, 'fitness': self.getGenome().fitness}
        return neat_info

    def save(self, filename):
        with open(filename+'.neat', 'wb') as _out:
            pickle.dump(self, _out, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename):
        with open(filename+'.neat', 'rb') as _in:
            return pickle.load(_in)
