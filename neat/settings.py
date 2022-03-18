from __future__ import annotations

import json

__version__ = '1.5.1'
__date__ = '18/03/2022'


class Settings(object):
    """
    Contains the default settings for NEAT, also has options
     to save and load values.
    """
    def __init__(self, directory: str, load: bool = True):
        """
        Initiates the object with default values and loads required
         settings from given file directory.
        :param directory: str
        :param load: bool
        """
        self.save_intervals = []
        self.delta_genome_threshold = 0.75
        self.distance_weights = {
            'connection': 1.0,
            'weight': 1.0,
            'bias': 1.0
        }
        self.node_info = {
            'activations': ['tanh'],
            'max_depth': 5,
            'max_backtrack': 1,
        }

        self.max_fitness = 0
        self.max_generations = 0
        self.max_fitness_history = 30

        self.kill = 0.7

        self.breed_probabilities = {
            'crossover': {'interspecies': 0.01,
                          'intraspecies': 0.1},
            'breed': {'asexual': 0.5,
                      'sexual': 0.5}
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

        self.load(directory) if load else self.save(directory)

    def load(self, directory='') -> None:
        """
        Loads the file and converts the json dict and updates
         the class
        :param directory: str
        :return:
            - None
        """
        with open(f"{directory}\\settings.json") as f:
            settings = json.load(f)
            self.__dict__.update(settings)

    def save(self, directory='') -> None:
        """
        Converts the class information into a json writable.
        :param directory: str
        :return:
            - None
        """
        with open(f"{directory}\\settings.json", 'w') as f:
            json.dump(self.__dict__, f, indent=4)
