import random

from neat.connection import Connection
from neat.node import Node
from neat import activations

__file__ = 'genome'
__version__ = '1.2'
__date__ = '02/03/2022'


class Genome(object):
    high, low = 1, -1

    def __init__(self, inputs, outputs, activation):
        self.inputs = inputs
        self.outputs = outputs
        self.activation = activation

        self.initial_nodes = inputs + outputs
        self.total_nodes = inputs + outputs

        self.connections = {}
        self.nodes = {}

        self.fitness = 0
        self.adjusted_fitness = 0

        self.generate()

    def generate(self):
        for n in range(self.total_nodes):
            self.nodes[n] = Node(self.activation)

        for i in range(self.inputs):
            for j in range(self.inputs, self.initial_nodes):
                self.addConnection((i, j), ((self.high - self.low) * random.random() + self.low))

    def forward(self, inputs):
        for i in range(self.inputs):
            self.nodes[i].output = inputs[i]

        nodes = {n: [] for n in range(self.total_nodes)}

        for pos in self.connections:
            if self.connections[pos].active:
                nodes[pos[1]].append(pos[0])

        input_nodes, hidden_nodes, output_nodes = self.getNodes()
        for j in hidden_nodes + output_nodes:
            node_sum = 0
            for i in nodes[j]:
                node_sum += self.connections[(i, j)].weight * self.nodes[i].output
            node = self.nodes[j]
            node.output = node.activation(node_sum + node.bias)
        return [self.nodes[n].output for n in range(self.inputs, self.initial_nodes)]

    def mutate(self, probabilities):
        self.addActiveConnection()

        population = list(probabilities.keys())
        probability_weights = [probabilities[mutation] for mutation in population]
        mutation = random.choices(population, weights=probability_weights)[0]
        input_nodes, hidden_nodes, output_nodes = self.getNodes()
        random_number = ((self.high - self.low) * random.random() + self.low)

        if mutation == "activation":
            self.activation = activations.getActivation()
        elif mutation == "node":
            self.addNode()
        elif mutation == "connection":
            self.addConnection(self.pair(input_nodes, hidden_nodes, output_nodes), random_number)
        elif mutation == "weight_perturb" or mutation == "weight_set":
            self.shiftWeight(mutation, random_number)
        elif mutation == "bias_perturb" or mutation == "bias_set":
            self.shiftBias(mutation, random_number, hidden_nodes + output_nodes)

        self.reset()

    def reset(self):
        for node in range(self.total_nodes):
            self.nodes[node].output = 0
        self.fitness = 0

    def addActiveConnection(self):
        disabled_connections = [conn for conn in self.connections if not self.connections[conn].active]
        if len(disabled_connections) == len(self.connections):
            self.connections[random.choice(disabled_connections)].active = True

    def addConnection(self, pos, weight):
        if pos in self.connections:
            self.connections[pos].active = True
        else:
            self.connections[pos] = Connection(weight)

    def addNode(self):
        pos = random.choice(self.getActiveConnections())
        connection = self.connections[pos]
        connection.active = False

        new_node = self.total_nodes
        self.nodes[new_node] = Node(self.activation)
        self.total_nodes += 1

        self.addConnection((pos[0], new_node), 1.0)
        self.addConnection((new_node, pos[1]), connection.weight)

    def pair(self, input_nodes, hidden_nodes, output_nodes):
        node_a = random.choice(input_nodes + hidden_nodes)
        join_to = [n for n in hidden_nodes + output_nodes if n != node_a]

        if join_to:
            node_b = random.choice(join_to)
        else:
            node_b = self.total_nodes
            self.addNode()
        return node_a, node_b

    def shiftWeight(self, mutation, random_number):
        connection = random.choice(list(self.connections.keys()))
        if mutation == "weight_perturb":
            self.connections[connection].weight += random_number
        elif mutation == "weight_set":
            self.connections[connection].weight = random_number

    def shiftBias(self, mutation, random_number, bias_nodes):
        node = random.choice(bias_nodes)
        if mutation == "bias_perturb":
            self.nodes[node].bias += random_number
        elif mutation == "bias_set":
            self.nodes[node].bias = random_number

    def getNodes(self):
        node_keys = list(self.nodes.keys())
        input_nodes = node_keys[:self.inputs]
        hidden_nodes = node_keys[self.initial_nodes:]
        output_nodes = node_keys[self.inputs:self.initial_nodes]
        return input_nodes, hidden_nodes, output_nodes

    def getActiveConnections(self, only_active=True):
        active_nodes, deactivated_nodes = [], []
        for pos in self.connections:
            if self.connections[pos].active:
                active_nodes.append(pos)
            else:
                deactivated_nodes.append(pos)
        if not only_active:
            return active_nodes, deactivated_nodes
        return active_nodes
