from __future__ import annotations

import random

from .activations import getActivation
from .gene import Node, Connection

import mattslib as ml
from mattslib.dict import getKeyByWeights

__version__ = '1.4.4'
__date__ = '11/04/2022'


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

        self.generate()

    def generate(self) -> None:
        """
        Generates the input and output nodes with depth and adds connections
         between nodes.
        :return:
            - None
        """
        for node_key in range(self.total_nodes):
            layer_type = self.LAYER_TYPES[0] if node_key < self.inputs else self.LAYER_TYPES[2]
            self.nodes[node_key] = Node(layer_type, self.activation)
            self.nodes[node_key].depth = 0 if layer_type == self.LAYER_TYPES[0] else self.max_depth

        for input_node in range(self.inputs):
            for output_node in range(self.inputs, self.initial_nodes):
                self.addConnection((input_node, output_node), ((self.HIGH - self.LOW) * random.random() + self.LOW))

    def forward(self, inputs: list) -> list:
        """
        Calculates the output sum using inputs, weights and bias.
        :param inputs: list[int | float]
        :return:
            - output - list[int | float]
        """
        for node_key in range(self.inputs):
            self.nodes[node_key].output = inputs[node_key]

        nodes = {node_key: [] for node_key in range(self.total_nodes)}

        for pos in self.connections:
            if self.connections[pos].active:
                nodes[pos[1]].append(pos[0])

        genome_nodes = self.getNodeByType(self.LAYER_TYPES[-2:])
        for node_out in genome_nodes[self.LAYER_TYPES[1]] + genome_nodes[self.LAYER_TYPES[2]]:
            node_sum = 0
            for node_in in nodes[node_out]:
                node_sum += self.connections[(node_in, node_out)].weight * self.nodes[node_in].output
            node = self.nodes[node_out]
            node.output = node.activation(node_sum + node.bias)
        return [self.nodes[n].output for n in range(self.inputs, self.initial_nodes)]

    def mutate(self, probabilities: dict) -> None:
        """
        Mutates a genomes gene, using given mutation probabilities.
        :param probabilities: dict[str: Any]
        :return:
            - None
        """
        node_types = self.getNodeByType()
        random_number = ((self.HIGH - self.LOW) * random.random() + self.LOW)

        mutation = getKeyByWeights(probabilities)
        node_key = random.choice(node_types[self.LAYER_TYPES[1]] + node_types[self.LAYER_TYPES[2]])
        if 'node' in mutation:
            if 'activation' in mutation:
                self.nodes[node_key].activation = getActivation(random.choice(self.activations))
            elif 'bias' in mutation:
                if 'set' in mutation:
                    self.nodes[node_key].bias = random_number
                elif 'adjust' in mutation:
                    self.nodes[node_key].bias += random_number
            elif 'add' in mutation:
                self.addNode()
            elif 'remove' in mutation:
                self.removeNode(node_key)
        elif 'connection' in mutation:
            pos = random.choice(list(self.connections.keys()))
            if 'active' in mutation:
                self.connections[pos].active = not self.connections[pos].active
            elif 'weight' in mutation:
                if 'set' in mutation:
                    self.connections[pos].weight = random_number
                elif 'adjust' in mutation:
                    self.connections[pos].weight += random_number
            elif 'add' in mutation:
                self.addConnection(self.pair(node_types[self.LAYER_TYPES[0]], node_types[self.LAYER_TYPES[1]],
                                             node_types[self.LAYER_TYPES[2]]), random_number)
            elif 'remove' in mutation:
                self.removeConnection()
        elif 'activation' in mutation:
            self.activation = getActivation(random.choice(self.activations))
        self.reset()

    def reset(self) -> None:
        """
        Resets the output for each node and the genome's fitness.
        :return:
            - None
        """
        for node_key in range(self.total_nodes):
            self.nodes[node_key].output = 0
        self.fitness = 0

    def addConnection(self, pos: tuple, weight: int | float) -> None:
        """
        Adds or activates the connection between given nodes.
        :param pos: tuple[int, int]
        :param weight: int | float
        :return:
            - None
        """
        if self.nodes[pos[1]].depth < self.nodes[pos[0]].depth:
            pos = pos[::-1]

        if pos in self.connections:  # checks forward connections
            self.connections[pos].active = True
        elif pos[::-1] in self.connections:  # checks side connections
            self.connections[pos[::-1]].active = True
        else:
            self.connections[pos] = Connection(weight)

    def removeConnection(self) -> None:
        """
        Removes an eligible connection form the network by weight pruning
        with the optimal brain damage strategy.
        :return:
            - None
        """
        inputs = [round(random.random(), 3) for _ in range(self.inputs)]
        outputs = self.forward(inputs)

        eligible_connections = []
        saliencies = {}
        for pos in list(self.connections.keys()):
            connected_from, connected_to = self.countConnected(pos)
            if connected_from >= 2 and connected_to >= 2:
                eligible_connections.append(pos)

        for pos in eligible_connections:
            self.connections[pos].active = False
            saliency = ml.list.difference(outputs, self.forward(inputs))
            saliencies[pos] = max([abs(i) for i in saliency])
            self.connections[pos].active = True

        if saliencies:
            min_pos = min(saliencies, key=saliencies.get)
            self.connections.pop(min_pos)

    def addNode(self) -> None:
        """
        Adds a new node inbetween an active connection, then removes the previous connections.
        :return:
            - None
        """
        new_node = self.total_nodes
        self.nodes[new_node] = Node(self.LAYER_TYPES[1], self.activation)
        pos = random.choice(self.getActiveConnections())

        depth = min(self.max_depth - 1, self.nodes[pos[0]].depth + 1)

        self.nodes[new_node].depth = depth
        self.total_nodes += 1
        self.addConnection((pos[0], new_node), 1.0)
        self.addConnection((new_node, pos[1]), self.connections[pos].weight)
        self.connections.pop(pos)

    def removeNode(self, node_key: int) -> None:
        """
        Removes a node from genome if the surrounding connections are sufficient.
        :param node_key: int
        :return:
            - None
        """
        connected_to, connected_from = self.getConnected(node_key)
        for pos in connected_to:
            if len(self.getConnected(pos)[1]) < 2:
                return
        for pos in connected_from:
            if len(self.getConnected(pos)[0]) < 2:
                return
        self.nodes.pop(node_key)
        self.total_nodes -= 1
        for pos in list(self.connections.keys()):
            if pos[0] == node_key or pos[1] == node_key:
                self.connections.pop(pos)

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

    def countConnected(self, connection: tuple) -> tuple:
        """
        Counts the surrounding connections.
        :param connection: tuple[int, int]
        :return:
            - connected_from, connected_to - tuple[int, int]
        """
        connected_from, connected_to = 0, 0
        for pos in self.connections:
            if connection[0] == pos[0]:
                connected_from += 1
            elif connection[1] == pos[1]:
                connected_to += 1
        return connected_from, connected_to

    def getConnected(self, node_key: int) -> tuple:
        """
        :param node_key: int
        :return:
            - connected_to, connected_from - tuple[list[tuple[int, int]], list[tuple[int, int]]]
        """
        connected_to, connected_from = [], []
        for pos in self.connections:
            if node_key == pos[0]:
                connected_from.append(pos)
            elif node_key == pos[1]:
                connected_to.append(pos)
        return connected_to, connected_from
