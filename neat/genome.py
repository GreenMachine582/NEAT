from __future__ import annotations

import random

from .activations import getActivation
from .gene import Node, Connection

from mattslib.dict import getKeyByWeights

__version__ = '1.5.2'
__date__ = '23/03/2022'


class Genome(object):
    """
    Genome is a Neural Network that evolves by mutating genes.
    """
    HIGH, LOW = 1, -1

    LAYER_TYPES = ['input', 'hidden', 'output']

    def __init__(self, inputs: int, outputs: int, node_info: dict):
        """
        Initiates the Genome object with values and generates the initial network.
        :param inputs: int
        :param outputs: int
        :param node_info: dict
        """
        self.inputs = inputs
        self.outputs = outputs
        self.node_info = node_info
        self.activations = node_info['activations']
        self.activation = getActivation(self.activations[0])

        self.initial_nodes = inputs + outputs
        self.total_nodes = inputs + outputs

        self.connections = {}
        self.nodes = {}

        self.fitness = 0
        self.adjusted_fitness = 0

        self.max_depth = node_info['max_depth']
        self.max_backtrack = node_info['max_backtrack']

        self.generate()

    def generate(self) -> None:
        """
        Generates the input and output nodes with depth and adds connections
         between nodes.
        :return:
            - None
        """
        for n in range(self.total_nodes):
            layer_type = self.LAYER_TYPES[0] if n < self.inputs else self.LAYER_TYPES[2]
            self.nodes[n] = Node(layer_type, self.activation)
            self.nodes[n].depth = 0 if layer_type == self.LAYER_TYPES[0] else self.max_depth

        for i in range(self.inputs):
            for j in range(self.inputs, self.initial_nodes):
                self.addConnection((i, j), ((self.HIGH - self.LOW) * random.random() + self.LOW))

    def forward(self, inputs: list) -> list:
        """
        Calculates the output sum using inputs, weights and bias.
        :param inputs: list[int | float]
        :return:
            - output - list[int | float]
        """
        for i in range(self.inputs):
            self.nodes[i].output = inputs[i]

        nodes = {n: [] for n in range(self.total_nodes)}

        for pos in self.connections:
            if self.connections[pos].active:
                nodes[pos[1]].append(pos[0])

        genome_nodes = self.getNodeByType(self.LAYER_TYPES[-2:])
        for j in genome_nodes[self.LAYER_TYPES[1]] + genome_nodes[self.LAYER_TYPES[2]]:
            node_sum = 0
            for i in nodes[j]:
                node_sum += self.connections[(i, j)].weight * self.nodes[i].output
            node = self.nodes[j]
            node.output = node.activation(node_sum + node.bias)
        return [self.nodes[n].output for n in range(self.inputs, self.initial_nodes)]

    def mutate(self, probabilities: dict) -> None:
        """
        Mutates a gene and a genome attribute using mutation probabilities.
        :param probabilities: dict[str: Any]
        :return:
            - None
        """
        self.addActiveConnection()
        node_types = self.getNodeByType()
        random_number = ((self.HIGH - self.LOW) * random.random() + self.LOW)

        mutate_gene = getKeyByWeights(probabilities['gene'])
        node = random.choice(node_types[self.LAYER_TYPES[1]] + node_types[self.LAYER_TYPES[2]])
        if 'node' in mutate_gene:
            if 'activation' in mutate_gene:
                self.nodes[node].activation = getActivation(random.choice(self.activations))
            elif 'bias' in mutate_gene:
                if 'set' in mutate_gene:
                    self.nodes[node].bias = random_number
                elif 'adjust' in mutate_gene:
                    self.nodes[node].bias += random_number
        if 'connection' in mutate_gene:
            pos = random.choice(list(self.connections.keys()))
            if 'active' in mutate_gene:
                self.connections[pos].active = not self.connections[pos].active
            if 'weight' in mutate_gene:
                if 'set' in mutate_gene:
                    self.connections[pos].weight = random_number
                elif 'adjust' in mutate_gene:
                    self.connections[pos].weight += random_number

        mutate_genome = getKeyByWeights(probabilities['genome'])
        if mutate_genome == 'activation':
            self.activation = getActivation(random.choice(self.activations))
        elif mutate_genome == 'node':
            self.addNode()
        elif mutate_genome == 'connection':
            self.addConnection(self.pair(node_types[self.LAYER_TYPES[0]], node_types[self.LAYER_TYPES[1]],
                                         node_types[self.LAYER_TYPES[2]]), random_number)

        self.reset()

    def reset(self) -> None:
        """
        Resets the output for each node and the genome's fitness.
        :return:
            - None
        """
        for node in range(self.total_nodes):
            self.nodes[node].output = 0
        self.fitness = 0

    def addActiveConnection(self) -> None:
        """
        Activates one of the deactivated connections.
        :return:
            - None
        """
        deactivated_connections = [pos for pos in self.connections if not self.connections[pos].active]
        if len(deactivated_connections) == len(self.connections):
            self.connections[random.choice(deactivated_connections)].active = True

    def addConnection(self, pos: tuple, weight: int | float) -> None:
        """
        Adds or activates the connection between given nodes and checks backtrack.
        :param pos: tuple[int, int]
        :param weight: int | float
        :return:
            - None
        """
        if pos in self.connections:
            self.connections[pos].active = True
        else:
            if self.nodes[pos[0]].depth > self.nodes[pos[1]].depth:
                if self.nodes[pos[0]].backtrack < self.max_backtrack:
                    self.nodes[pos[1]].backtrack += 1
                else:
                    pos = pos[::-1]
            self.connections[pos] = Connection(weight)

    def addNode(self) -> None:
        """
        Adds a random node to the genome.
        :return:
            - None
        """
        new_node = self.total_nodes
        self.nodes[new_node] = Node(self.LAYER_TYPES[1], self.activation)

        pos = random.choice(self.getActiveConnections())
        connection = self.connections[pos]
        connection.active = False

        depth = min(self.max_depth - 1, self.nodes[pos[0]].depth + 1)

        self.nodes[new_node].depth = depth
        self.total_nodes += 1
        self.addConnection((pos[0], new_node), 1.0)
        self.addConnection((new_node, pos[1]), connection.weight)

    def pair(self, input_nodes: list, hidden_nodes: list, output_nodes: list) -> tuple:
        """
        Finds two nodes that can form a connection or adds a new node.
        :param input_nodes: list[int]
        :param hidden_nodes: list[int]
        :param output_nodes: list[int]
        :return:
            - node_a, node_b - tuple[int, int]
        """
        node_a = random.choice(input_nodes + hidden_nodes)
        join_to = [n for n in hidden_nodes + output_nodes if n != node_a]

        if join_to:
            node_b = random.choice(join_to)
        else:
            node_b = self.total_nodes
            self.addNode()
        return node_a, node_b

    def getNodeByType(self, layer_types: list = None) -> dict:
        """
        Sorts the nodes but layer type.
        :param layer_types: list[str]
        :return:
            - node_types - dict[str: list[int]]
        """
        if layer_types is None:
            layer_types = self.LAYER_TYPES
        node_types = {node_type: [] for node_type in layer_types}

        for node_key in self.nodes:
            if self.nodes[node_key].layer_type in node_types:
                node_types[self.nodes[node_key].layer_type].append(node_key)
        return node_types

    def getNodesByDepth(self) -> dict:
        """
        Sorts the nodes by node depth.
        :return:
            - node_depths - dict[int: list[int]]
        """
        node_depths = {i: [] for i in range(self.max_depth + 1)}
        for node_key in self.nodes:
            node = self.nodes[node_key]
            node_depths[node.depth].append(node_key)
        return node_depths

    def getActiveConnections(self) -> list:
        """
        Gets the active connections.
        :return:
            - list[tuple[int, int]]
        """
        return [pos for pos in self.connections if self.connections[pos].active]
