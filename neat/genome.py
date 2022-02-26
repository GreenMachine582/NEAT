import random

from neat.connection import Connection
from neat.node import Node


class Genome(object):
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

    def generate(self, high=1, low=-1):
        for n in range(self.total_nodes):
            self.nodes[n] = Node(self.activation)

        for i in range(self.inputs):
            for j in range(self.inputs, self.initial_nodes):
                self.addConnection((i, j), ((high - low) * random.random() + low))

    def forward(self, inputs):
        if len(inputs) != self.inputs:
            print("Incorrect number of inputs.")
            quit()

        for i in range(self.inputs):
            self.nodes[i].output = inputs[i]

        nodes = {n: [] for n in range(self.total_nodes)}

        for pos in self.connections:
            if self.connections[pos].active:
                nodes[pos[1]].append(pos[0])

        node_keys = list(self.nodes.keys())
        hidden_nodes = node_keys[self.initial_nodes:]
        output_nodes = node_keys[self.inputs:self.initial_nodes]
        for j in hidden_nodes + output_nodes:
            node_sum = 0
            for i in nodes[j]:
                node_sum += self.connections[(i, j)].weight * self.nodes[i].output
            node = self.nodes[j]
            node.output = node.activation(node_sum + node.bias)
        return [self.nodes[n].output for n in range(self.inputs, self.initial_nodes)]

    def evaluate(self):
        pass

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
        self.total_nodes += 1
        self.nodes[new_node] = Node(self.activation)

        self.addConnection((pos[0], new_node), 1.0)
        self.addConnection((new_node, pos[1]), connection.weight)

    def getActiveConnections(self):
        active_nodes = []
        for pos in self.connections:
            if self.connections[pos].active:
                active_nodes.append(pos)
        return active_nodes
