from setuptools import setup

setup(
    name='NEAT',
    version='1.5',
    author='Matthew Johnson',
    author_email='greenmachine1902@gmail.com',
    url='https://github.com/greenmachine1902/NEAT',
    license="BSD",
    description='Application of a NEAT with Connect 4',
    long_description='Application of a NEAT (NeuroEvolution of Augmenting Topologies) with a Connect 4 environment',
    packages=['connect4', 'connect4/models', 'mattslib', 'mattslib/pygame', 'neat'],
)
