import random

from .connection import Connection
from .node import Node
from .activations import getActivation

__file__ = 'genome'
__version__ = '1.3'
__date__ = '10/03/2022'


class Genome(object):
    high, low = 1, -1

    def __init__(self, inputs, outputs, node_info):
        self.inputs = inputs
        self.outputs = outputs
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

    def generate(self):
        for n in range(self.total_nodes):
            self.nodes[n] = Node(self.activation)
            self.nodes[n].depth = 0 if self.getNodeType(n) == 'input' else self.max_depth

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

        genome_nodes = self.getNodes(['hidden', 'output'])
        for j in genome_nodes['hidden'] + genome_nodes['output']:
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
        nodes = self.getNodes()
        random_number = ((self.high - self.low) * random.random() + self.low)

        if mutation == "activation":
            self.activation = getActivation(random.choice(self.activations))
        elif mutation == "node":
            self.addNode()
        elif mutation == "connection":
            self.addConnection(self.pair(nodes['input'], nodes['hidden'], nodes['output']), random_number)
        elif mutation == "weight_perturb" or mutation == "weight_set":
            self.shiftWeight(mutation, random_number)
        elif mutation == "bias_perturb" or mutation == "bias_set":
            self.shiftBias(mutation, random_number, nodes['hidden'] + nodes['output'])

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
            # > limit backtrack. >= limit backtrack and side connection
            if self.nodes[pos[0]].depth >= self.nodes[pos[1]].depth:
                if self.nodes[pos[0]].backtrack < self.max_backtrack:
                    self.nodes[pos[1]].backtrack += 1
                else:
                    pos = pos[::-1]
            self.connections[pos] = Connection(weight)

    def addNode(self):
        new_node = self.total_nodes
        self.nodes[new_node] = Node(self.activation)

        pos = random.choice(self.getActiveConnections())
        connection = self.connections[pos]
        connection.active = False

        # depth = random.randint
        depth = min(self.max_depth - 1, self.nodes[pos[0]].depth + 1)

        self.nodes[new_node].depth = depth
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

    def getNodes(self, node_types=None):
        if node_types is None:
            node_types = ['input', 'hidden', 'output']
        node_keys = list(self.nodes.keys())
        out_nodes = {}
        if 'input' in node_types:
            out_nodes['input'] = node_keys[:self.inputs]
        if 'hidden' in node_types:
            out_nodes['hidden'] = node_keys[self.initial_nodes:]
        if 'output' in node_types:
            out_nodes['output'] = node_keys[self.inputs:self.initial_nodes]
        return out_nodes

    def getNodesByDepth(self):
        node_depths = {}
        for node_key in self.nodes:
            node = self.nodes[node_key]
            if node.depth not in node_depths.keys():
                node_depths[node.depth] = []
            node_depths[node.depth].append(node_key)
        return node_depths

    def getNodeType(self, node_index):
        node_keys = list(self.nodes.keys())
        if node_index in (node_keys[:self.inputs]):
            return 'input'
        elif node_index in (node_keys[self.inputs: self.inputs + self.outputs]):
            return 'output'
        return 'hidden'

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
