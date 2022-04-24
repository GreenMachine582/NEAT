# NEAT v1.6.5
Application of a NEAT (NeuroEvolution of Augmenting Topologies) with a Connect 4 environment.


## Basic Usage
Setup:
```python
from neat import NEAT
neat = NEAT(ENVIRONMENT_DIR)
neat.generate(2, 1, population=100)
```
Changing Settings:
```python
neat.settings.max_fitness = 1000
neat.settings.save_intervals = [1, 5, 5000, 10000]
neat.settings.mutation_probabilities['node_activation'] = 0.4
```
Iterate Populace:
```python
while neat.shouldEvolve():
    current_genome = neat.getGenome()
    result = current_genome.forward([2, 4])
    current_genome.fitness = 3
    neat.nextGenome()
```
Parallel:
```python
results = neat.parallelTest(environment, args)
neat.parallelEvolve(fitnessEvaluation, results, args)
```
Get Best:
```python
best_genome = neat.best_specie.representative
```
```python
best_genome = neat.best_genome
```