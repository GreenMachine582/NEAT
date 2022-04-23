from __future__ import annotations

from math import ceil
import random

from .activations import getActivation
from .gene import Node, Connection

import mattslib as ml
from mattslib.dict import getKeyByWeights

__version__ = '1.4.6'
__date__ = '23/04/2022'


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
        self.total_connections = inputs * outputs

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

        nodes = {node_key: [] for node_key in self.nodes}

        active_connections = self.getActiveConnections()
        for pos in active_connections:
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
                if not self.addNode():
                    self.mutate(probabilities)
            elif 'remove' in mutation:
                self.removeNode(node_key)
        elif 'connection' in mutation:
            pos = random.choice(list(self.connections))
            if 'weight' in mutation:
                if 'set' in mutation:
                    self.connections[pos].weight = random_number
                elif 'adjust' in mutation:
                    self.connections[pos].weight += random_number
            elif 'add' in mutation:
                self.addConnection(self.pair(), random_number)
            elif 'remove' in mutation:
                if not self.removeConnection():
                    self.mutate(probabilities)
        elif 'activation' in mutation:
            self.activation = getActivation(random.choice(self.activations))
        self.reset()

    def reset(self) -> None:
        """
        Resets the output for each node and the genome's fitness.
        :return:
            - None
        """
        for node_key in self.nodes:
            self.nodes[node_key].output = 0
        self.fitness = 0

    def addConnection(self, pos: tuple, weight: int | float) -> bool:
        """
        Adds a new connection between the given nodes.
        :param pos: tuple[int, int]
        :param weight: int | float
        :return:
            - added - bool
        """
        pos = self.checkPair(pos)
        if pos is None:
            return False

        # Adds the new connection
        self.connections[pos] = Connection(weight)
        self.total_connections += 1
        return True

    def removeConnection(self) -> bool:
        """
        Removes an eligible connection form the genome by weight pruning with
        the optimal brain damage strategy.
        :return:
            - removed - bool
        """
        eligible_connections = []
        for pos in self.connections:
            connected_from, connected_to = self.countConnected(pos)
            if connected_from > 1 and connected_to > 1:
                eligible_connections.append(pos)

        if not eligible_connections:
            return False

        inputs = [round(random.random(), 3) for _ in range(self.inputs)]
        outputs = self.forward(inputs)
        saliencies = {}
        for pos in eligible_connections:
            self.connections[pos].active = False
            saliency = ml.list.difference(outputs, self.forward(inputs))
            saliencies[pos] = max([abs(i) for i in saliency])
            self.connections[pos].active = True

        if saliencies:
            min_pos = min(saliencies, key=saliencies.get)
            self.connections.pop(min_pos)
            self.total_connections -= 1
            return True
        return False

    def addNode(self) -> bool:
        """
        Adds a new node inbetween an active connection, then removes the previous
        connection.
        :return:
            - added - bool
        """
        # Finds a midpoint depth inbetween an active connection
        pos = random.choice(self.getActiveConnections())
        depth = ceil((self.nodes[pos[0]].depth + self.nodes[pos[1]].depth) / 2)
        if self.nodes[pos[0]].depth < depth < self.nodes[pos[1]].depth:
            # Adds the new node and two new connections
            node_key = self.total_nodes
            self.nodes[node_key] = Node(self.LAYER_TYPES[1], self.activation)
            self.nodes[node_key].depth = depth
            self.total_nodes += 1
            self.addConnection((pos[0], node_key), 1.0)
            self.addConnection((node_key, pos[1]), self.connections[pos].weight)
            self.connections.pop(pos)  # removes the previous connection
            self.total_connections -= 1
            return True
        return False

    def removeNode(self, node_key: int) -> bool:
        """
        Removes a node from genome if the surrounding connections are sufficient.
        :param node_key: int
        :return:
            - removes - bool
        """
        if self.nodes[node_key].layer_type != self.LAYER_TYPES[1]:
            return False

        connected_to, connected_from = self.getConnected(node_key)
        for pos in connected_to:
            if self.countConnected(pos)[0] == 1:
                self.connections[(pos[0], connected_from[0][1])] = self.connections[pos]
        for pos in connected_from:
            if self.countConnected(pos)[1] == 1:
                self.connections[(connected_to[0][0], pos[1])] = self.connections[pos]

        for pos in connected_to + connected_from:
            self.connections.pop(pos)

        self.nodes.pop(node_key)
        self.total_nodes -= 1

        # Updates the nodes and connections keys
        self.updateKeys()
        self.total_connections = len(self.connections)
        return True

    def updateKeys(self) -> None:
        """
        Updates node keys and connection keys that are out of bounds.
        :return:
            - None
        """
        max_node_key = max(list(self.nodes))
        if max_node_key >= self.total_nodes:
            for node_key in range(self.total_nodes):
                if node_key not in self.nodes:
                    self.nodes[node_key] = self.nodes[max_node_key]
                    self.nodes.pop(max_node_key)
                    for pos in list(self.connections):
                        if max_node_key == pos[0]:
                            self.connections[(node_key, pos[1])] = self.connections[pos]
                            self.connections.pop(pos)
                        elif max_node_key == pos[1]:
                            self.connections[(pos[0], node_key)] = self.connections[pos]
                            self.connections.pop(pos)
                    return

    def pair(self) -> tuple:
        """
        Finds a pair of nodes that can form a connection.
        :return:
            - pos - tuple[int, int]
        """
        while True:
            node_a = random.randrange(self.total_nodes)
            node_b = random.randrange(self.total_nodes)
            pos = self.checkPair((node_a, node_b))
            if pos is not None:
                return pos

    def checkPair(self, pos: tuple) -> tuple:
        """
        Checks if the given connection is valid.
        :param pos: tuple[int, int]
        :return:
            - pos - tuple[int, int] | None
        """
        if pos[0] != pos[1]:
            if self.nodes[pos[0]].depth < self.nodes[pos[1]].depth:
                return pos
            elif self.nodes[pos[1]].depth < self.nodes[pos[0]].depth:
                return pos[::-1]

    def getNodeByType(self, layer_types: list = None) -> dict:
        """
        Sorts the nodes by layer type.
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
            if connection[1] == pos[1]:
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
            if node_key == pos[1]:
                connected_to.append(pos)
        return connected_to, connected_from
