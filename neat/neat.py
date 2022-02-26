from neat.settings import Settings
from neat.genome import Genome
from neat.specie import Specie
import neat.activations as activations

__file__ = 'neat'
__version__ = '1.0.0'
__date__ = '26/02/2022'


def genomicDistance(x_member, y_member, distance_weights):
    x_connections = list(x_member.connections)
    y_connections = list(y_member.connections)

    connections = {}
    for c in x_connections + y_connections:
        if c not in connections:
            connections[c] = 1
        else:
            connections[c] += 1

    matching_connections = [i for i in connections if connections[i] == 2]
    disjoint_connections = [i for i in connections if connections[i] == 1]
    count_connections = len(max(x_connections, y_connections))
    count_nodes = min(x_member.total_nodes, y_member.total_nodes)

    weight_diff = 0
    for i in matching_connections:
        weight_diff += abs(x_member.connections[i].weight - y_member.connections[i].weight)

    bias_diff = 0
    for i in range(count_nodes):
        bias_diff += abs(x_member.nodes[i].bias - y_member.nodes[i].bias)

    t1 = distance_weights['edge'] * len(disjoint_connections)/count_connections
    t2 = distance_weights['weight'] * weight_diff/len(matching_connections)
    t3 = distance_weights['bias'] * bias_diff/count_nodes
    return t1 + t2 + t3


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

        self.global_best = None

    def generate(self, inputs, outputs, population=100):
        self.inputs = inputs
        self.outputs = outputs
        self.population = population

        for _ in range(self.population):
            genome = Genome(self.inputs, self.outputs, activations.get_activation(self.settings.activation))
            self.classify_genome(genome)

        self.global_best = self.species[0].members[0]

    def classify_genome(self, genome):
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
