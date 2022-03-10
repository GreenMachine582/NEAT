import json

__file__ = 'settings'
__version__ = '1.3'
__date__ = '08/03/2022'


class Settings(object):
    def __init__(self, directory):
        self.delta_genome_threshold = 0.75
        self.distance_weights = {
            'connection': 1.0,
            'weight': 1.0,
            'bias': 1.0
        }
        self.activations = ['leakyReLU']
        self.max_depth = 4
        self.max_backtrack = 1

        self.max_fitness = 0
        self.max_generations = 0
        self.max_fitness_history = 30

        self.breed_probabilities = {
            'asexual': 0.5,
            'sexual': 0.5
        }
        self.mutation_probabilities = {
            'activation': 0.01,
            'node': 0.01,
            'connection': 0.09,
            'weight_perturb': 0.4,
            'weight_set': 0.1,
            'bias_perturb': 0.3,
            'bias_set': 0.1
        }
        self.load(directory)

    def load(self, directory=''):
        with open(directory + 'settings.json') as f:
            settings = json.load(f)
            self.__dict__.update(settings)

    def save(self, directory=''):
        with open(directory + 'settings.json', 'w') as f:
            json.dump(self.__dict__, f, indent=4)
