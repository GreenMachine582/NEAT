from __future__ import annotations

from copy import deepcopy
import pickle
import random

from .genome import Genome
from .settings import Settings
from .specie import Specie
from mattslib.dict import countOccurrence

__version__ = '1.4'
__date__ = '17/03/2022'


def genomicDistance(x_member: Genome, y_member: Genome, distance_weights: dict) -> float:
    """
    Calculations the distance between the given genomes.
    :param x_member: Genome
    :param y_member: Genome
    :param distance_weights: dict[str: int | float]
    :return:
        - distance - float
    """
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


def genomicCrossover(x_member: Genome, y_member: Genome) -> Genome:
    """
    Breeds a child genome from the given parent genomes.
    :param x_member: Genome
    :param y_member: Genome
    :return:
        - child - Genome
    """
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
    """
    NEAT (NeuroEvolution of Augmenting Topologies) is a genetic algorithm
     that evolves neural networks. The neural networks are seen as genomes
     and its parameters and attributes are evolved as genes.
    """

    def __init__(self, settings_dir: str = ''):
        """
        Initiates the NEAT object with default and given values.
        :param settings_dir:
        """
        self.settings = Settings(settings_dir)
        self.inputs = 0
        self.outputs = 0

        self.species = []
        self.population = 0

        self.generation = 0
        self.current_species = 0
        self.current_genome = 0

        self.best_genome = None

    def generate(self, inputs: int, outputs: int, population: int = 100) -> None:
        """
        Generates the NEAT with given values and classifies the genomes
         into species.
        :param inputs: int
        :param outputs: int
        :param population: int
        :return:
            - None
        """
        self.inputs = inputs
        self.outputs = outputs
        self.population = population

        for _ in range(self.population):
            genome = Genome(self.inputs, self.outputs, self.settings.node_info)
            self.classifyGenome(genome)

        self.best_genome = self.species[0].members[0]

    def classifyGenome(self, genome: Genome) -> None:
        """
        Classifies the genome and groups it with similar species or creates
         a new specie.
        :param genome: Genome
        :return:
            - None
        """
        classified = False
        if len(self.species) > 0:
            for specie in self.species:
                representative_of_specie = specie.members[0]
                distance = genomicDistance(genome, representative_of_specie, self.settings.distance_weights)
                if distance <= self.settings.delta_genome_threshold:
                    specie.members.append(genome)
                    classified = True
        if not classified:
            self.species.append(Specie(self.settings.max_fitness_history, genome))

    def updateFitness(self) -> None:
        """
        Updates the best fitness and genome from leading genomes within
         each specie.
        :return:
            - None
        """
        leading_genomes = [specie.getBest() for specie in self.species]
        best_genome = leading_genomes[0]
        for leading_genome in leading_genomes:
            if leading_genome.fitness > best_genome.fitness:
                best_genome = leading_genome
        self.best_genome = deepcopy(best_genome)

    def breed(self, probabilities: dict, specie_key: int) -> Genome:
        """
        Breeds a new genome with given probabilities.
        :param probabilities: dict[str: dict[str: int]]
        :param specie_key: int
        :return:
            - child - Genome
        """
        crossover_by = random.choices(list(probabilities['crossover'].keys()),
                                      weights=list(probabilities['crossover'].values()))[0]
        breed_by = random.choices(list(probabilities['breed'].keys()),
                                  weights=list(probabilities['breed'].values()))[0]

        x_member, y_member = None, None
        if crossover_by == 'intraspecies' or breed_by == 'asexual' or len(self.species) < 2:
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

    def killPopulation(self) -> None:
        """
        Removes species that had unfavorable fitness results and then removes
         a portion of genomes.
        :return:
            - None
        """
        surviving_species = []
        for specie in self.species:
            if specie.shouldSurvive():
                surviving_species.append(specie)
        self.species = surviving_species

        for specie in self.species:
            specie.killGenomes(self.settings.kill)

    def repopulate(self, fitness_sum: int | float) -> None:
        """
        Repopulates the population by breeding new child genomes, clones the
         best genome or creates fresh genomes.
        :param fitness_sum: int | float
        :return:
            - None
        """
        if len(self.species) > 0:
            for specie_key, specie in enumerate(self.species):
                offspring = int(round((specie.fitness_mean / fitness_sum) * (self.population - self.getPopulation())))
                for _ in range(offspring):
                    child = self.breed(self.settings.breed_probabilities, specie_key)
                    self.classifyGenome(child)
        else:
            for p in range(self.population):
                genome = deepcopy(self.best_genome) if p % 3 == 0 else Genome(self.inputs, self.outputs,
                                                                              self.settings.node_info)
                genome.mutate(self.settings.mutation_probabilities)
                self.classifyGenome(genome)

    def evolve(self) -> None:
        """
        Updates the fitness for each specie, if no progress has been made then
         mutate, else kill a portion of the population and repopulate.
        :return:
            - None
        """
        fitness_sum = 0
        for specie in self.species:
            specie.updateFitness()
            fitness_sum += specie.fitness_mean

        if fitness_sum <= 0:
            for specie in self.species:
                for member in specie.members:
                    member.mutate(self.settings.mutation_probabilities)
        else:
            self.killPopulation()
            self.repopulate(fitness_sum)
        self.generation += 1

    def shouldEvolve(self) -> bool:
        """
        Checks the settings if the current NEAT meets requirements to
         continue evolving.
        :return:
            - bool - True | False
        """
        self.updateFitness()
        if self.settings.max_generations and self.generation >= self.settings.max_generations:
            if self.settings.max_fitness and self.best_genome.fitness >= self.settings.max_fitness:
                return False
        return True

    def nextGenome(self) -> None:
        """
        Gets the next genome in population and updates counters.
        :return:
        """
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

    def getGenome(self, specie: int = None, genome: int = None) -> Genome:
        """
        Returns the current genome or requested genome.
        :param specie: int
        :param genome: int
        :return:
            - genome - Genome
        """
        specie = self.current_species if specie is None else specie
        genome = self.current_genome if genome is None else genome
        return self.species[specie].members[genome]

    def getPopulation(self) -> int:
        """
        Returns the current population.
        :return:
            - population - int
        """
        return sum([len(specie.members) for specie in self.species])

    def getInfo(self) -> dict:
        """
        Returns the current NEAT information.
        :return:
            - neat_info - dict[str: int | float]
        """
        neat_info = {'generation': self.generation+1, 'current_species': self.current_species+1,
                     'current_genome': self.current_genome+1, 'fitness': self.getGenome().fitness}
        return neat_info

    def save(self, filename: str) -> None:
        """
        Saves the NEAT object to file.
        :param filename: str
        :return:
            - None
        """
        with open(filename+'.neat', 'wb') as neat_file:
            pickle.dump(self, neat_file, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename: str) -> NEAT:
        """
        Loads the NEAT object from file.
        :param filename: str
        :return:
            - neat - NEAT
        """
        with open(filename+'.neat', 'rb') as neat_file:
            return pickle.load(neat_file)
