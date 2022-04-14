from __future__ import annotations

from copy import deepcopy
import random

from .genome import Genome
from .settings import Settings
from .specie import Specie, genomicDistance
from mattslib.dict import countOccurrence, getKeyByWeights
from mattslib.file import read, write

__version__ = '1.4.8'
__date__ = '14/04/2022'


def genomicCrossover(x_member: Genome, y_member: Genome) -> Genome:
    """
    Breeds a child genome from the given parent genomes.
    :param x_member: Genome
    :param y_member: Genome
    :return:
        - child - Genome
    """
    child = Genome(x_member.inputs, x_member.outputs, x_member.node_info)
    child.nodes = deepcopy(x_member.nodes)
    child.total_nodes = x_member.total_nodes
    child.connections = {}

    # Copy eligible connections
    for pos in y_member.connections:
        for connection in [pos, pos[::-1]]:
            if connection[0] < child.total_nodes and connection[1] < child.total_nodes:
                if child.nodes[connection[0]].depth < child.nodes[connection[1]].depth:
                    child.connections[connection] = deepcopy(y_member.connections[pos])

    # Fill in remaining possible connections
    for pos in x_member.connections:
        if pos not in list(child.connections):
            child.connections[pos] = deepcopy(x_member.connections[pos])

    child.total_connections = len(child.connections)
    child.reset()
    return child


class NEAT(object):
    """
    NEAT (NeuroEvolution of Augmenting Topologies) is a genetic algorithm
     that evolves neural networks. The neural networks are seen as genomes
     and its parameters and attributes are evolved as genes.
    """

    def __init__(self, environment_dir: str):
        """
        Initiates the NEAT object with default and given values.
        :param environment_dir: str
        """
        self.settings = Settings(environment_dir)
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

        # Creates and specifies the populace
        for _ in range(self.population):
            genome = Genome(self.inputs, self.outputs, self.settings.node_info)
            self.classifyGenome(genome)

        self.best_genome = self.species[0].members[0]

    def nextGenome(self, filename: str) -> bool:
        """
        Gets the next genome in population, updates counters and
        saves models at certain intervals.
        :param filename: str
        :return:
            - new_generation - bool
        """
        specie = self.species[self.current_species]
        if self.current_genome < len(specie.members) - 1:
            self.current_genome += 1
        else:
            self.current_genome = 0
            if self.current_species < len(self.species) - 1:
                self.current_species += 1
            else:
                self.evolve()
                self.current_species = 0
                self.save(f"{filename}")
                if self.generation in self.settings.save_intervals:
                    self.save(f"{filename}_gen_{self.generation}")
                elif self.settings.save_model_interval != 0 and\
                        self.generation % self.settings.save_model_interval == 0:
                    self.save(f"{filename}_gen_{self.generation}")
                return True
        return False

    def shouldEvolve(self) -> bool:
        """
        Checks the settings if the current NEAT meets requirements to
        continue evolving.
        :return:
            - should_evolve - bool
        """
        self.updateBestGenome()
        if self.settings.max_generations != 0 and self.generation >= self.settings.max_generations:
            return False
        if self.settings.max_fitness != 0 and self.best_genome.fitness >= self.settings.max_fitness:
            return False
        return True

    def evolve(self, minimum_fitness: int = 0) -> None:
        """
        Evolves the NEAT by culling, repopulating and mutating the populace.
        :param minimum_fitness: int
        :return:
            - None
        """
        for specie in self.species:
            specie.updateFitness()
            specie.updateFitnessHistory()
            specie.updateRepresentative()

        if self.getFitnessSum() > minimum_fitness:
            kill_species = []
            for specie_key, specie in enumerate(self.species):
                if not self.cullPopulation(specie):
                    kill_species.append(specie_key)

            for specie_key in kill_species[::-1]:
                self.species.pop(specie_key)

            self.repopulate()
        else:
            # Mutates all genomes since fitness didn't reach minimum requirements
            for specie in self.species:
                for member in specie.members:
                    member.mutate(self.settings.mutation_probabilities)
        self.generation += 1

    def cullPopulation(self, specie: Specie) -> bool:
        """
        Culls the population by selective killing, either removing the specie as a whole,
        removing duplicate members or kill a portion of the species members.
        :param specie: Specie
        :return:
            - survive - bool
        """
        # Kills specie that did not meet minimum requirements
        if not specie.shouldSurvive():
            return False

        remove_duplicate = False
        if self.generation % self.settings.remove_duplicate_interval == 0 and self.generation != 0:
            remove_duplicate = True
        specie.killGenomes(remove_duplicate)
        specie.updateRepresentative()
        return True

    def repopulate(self) -> None:
        """
        Repopulates the populace by breeding new child genomes, cloning the
        best genome or creates fresh genomes with mutations.
        :return:
            - None
        """
        if self.species:
            for specie in self.species:
                specie.updateFitness()
            fitness_sum = self.getFitnessSum()

            # Breeds the surviving populace
            temp_species = self.species[:]
            for specie_key, specie in enumerate(temp_species):
                if fitness_sum != 0:
                    population_diff = self.population - self.getPopulation()
                    offspring = round((specie.fitness_mean / fitness_sum) * population_diff)
                    fitness_sum -= specie.fitness_mean
                    for _ in range(offspring):
                        child = self.breed(self.settings.breed_probabilities, specie)
                        self.classifyGenome(child)

        # Introduces new species and genomes if populace is not restored
        for p in range(self.population - self.getPopulation()):
            genome = deepcopy(self.best_genome) if p % 3 == 0 else Genome(self.inputs, self.outputs,
                                                                          self.settings.node_info)
            genome.mutate(self.settings.mutation_probabilities)
            self.classifyGenome(genome)

    def breed(self, probabilities: dict, specie: Specie) -> Genome:
        """
        Breeds a new genome with given probabilities.
        :param probabilities: dict[str: dict[str: int]]
        :param specie: Specie
        :return:
            - child - Genome
        """
        breed_by = getKeyByWeights(probabilities['breed'])
        # Asexual
        if breed_by == "asexual" or len(specie.members) == 1:
            child = deepcopy(random.choice(specie.members))
            child.mutate(self.settings.mutation_probabilities)
            return child

        # Sexual
        crossover_by = getKeyByWeights(probabilities['crossover'])
        if crossover_by == 'intraspecies' or len(self.species) < 2:
            (x_member, y_member) = random.sample(specie.members, 2)
        else:  # interspecies
            species = [i for i in self.species if i != specie]
            x_member = random.choice(specie.members)
            y_member = random.choice(random.choice(species).members)
        return genomicCrossover(x_member, y_member)

    def classifyGenome(self, genome: Genome) -> None:
        """
        Classifies the genome into first similar species or creates a new specie.
        :param genome: Genome
        :return:
            - None
        """
        for specie in self.species:
            distance = genomicDistance(genome, specie.representative, self.settings.distance_weights)
            if distance <= self.settings.delta_genome_threshold:
                specie.members.append(genome)
                return
        self.species.append(Specie(self.settings, genome))
        return

    def updateBestGenome(self) -> None:
        """
        Updates the best genome by searching for the highest fitness from
        each specie.
        :return:
            - None
        """
        for specie in self.species:
            if specie.representative.fitness > self.best_genome.fitness:
                self.best_genome = deepcopy(specie.representative)

    def getFitnessSum(self) -> int | float:
        """
        Sums each species mean fitness.
        :return:
            - fitness_sum - int | float
        """
        fitness_sum = 0
        for specie in self.species:
            fitness_sum += specie.fitness_mean
        return fitness_sum

    def getGenome(self) -> Genome:
        """
        Returns the current genome.
        :return:
            - genome - Genome
        """
        return self.species[self.current_species].members[self.current_genome]

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

    def update(self, **kwargs: Any) -> None:
        """
        Updates the best genome by searching for the highest fitness from
        each specie.
        :param kwargs: Any
        :return:
            - None
        """
        if 'environment_dir' in kwargs:
            self.settings = Settings(kwargs['environment_dir'])

    def save(self, file_dir: str) -> None:
        """
        Saves the NEAT object by writing to file.
        :param file_dir: str
        :return:
            - None
        """
        write(self, file_dir + '.neat')

    @staticmethod
    def load(file_dir: str) -> NEAT:
        """
        Loads the NEAT object by reading the file.
        :param file_dir: str
        :return:
            - neat - NEAT
        """
        return read(file_dir + '.neat')
