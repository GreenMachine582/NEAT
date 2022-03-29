from __future__ import annotations

from mattslib.file import read, write

__version__ = '1.4.4'
__date__ = '28/03/2022'


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
            'activation': 0.1,
            'node': 0.5,
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
        self.remove_duplicate_interval = 50
        self.duplicate_distance_threshold = 0.001

        self.breed_probabilities = {
            'crossover': {'interspecies': 0.01,
                          'intraspecies': 0.1},
            'breed': {'asexual': 0.5,
                      'sexual': 0.5}
        }
        self.mutation_probabilities = {
            'gene': {'node_activation': 0.1,
                     'node_bias_adjust': 0.3,
                     'node_bias_set': 0.1,
                     'connection_active': 0.05,
                     'connection_weight_adjust': 0.4,
                     'connection_weight_set': 0.1},
            'genome': {'activation': 0.01,
                       'node': 0.01,
                       'connection': 0.09},
        }

        self.load(directory) if load else self.save(directory)

    def load(self, directory='') -> None:
        """
        Loads the file and converts the json dict and updates
        the class.
        :param directory: str
        :return:
            - None
        """
        self.__dict__.update(read(f"{directory}\\settings.json"))

    def save(self, directory='') -> None:
        """
        Converts the class information into a json writable.
        :param directory: str
        :return:
            - None
        """
        write(self.__dict__, f"{directory}\\settings.json")
