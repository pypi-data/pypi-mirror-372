#!/usr/bin/env python3

import os
from .hub_component import HubComponent
from .genome import Genome


class Hub(HubComponent):

    default_kwargs = {
        "genomesFile": "genomes.txt",
    }
    required_keys = ["hub", "shortLabel", "longLabel", "genomesFile", "email"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.genomes = []
        
    def add_genome(self, genome: Genome):

        if not isinstance(genome, Genome):
            raise ValueError(f"Genome must be an instance of Genome, not {type(genome)}.")

        genome.hub = self
        self.genomes.append(genome)
    
    def generate(self, target_path=""):

        os.makedirs(os.path.join(target_path, self.kwargs["hub"]), exist_ok=True)

        # generate hub.txt
        with open(os.path.join(target_path, self.kwargs["hub"], "hub.txt"), "w") as hub_f:
            hub_f.write(self.format())

        # generate genomes.txt
        with open(os.path.join(target_path, self.kwargs["hub"], "genomes.txt"), "w") as genomes_f:
            for genome in self.genomes:
                genomes_f.write(genome.format())
                genome.generate(target_path=os.path.join(target_path, self.kwargs["hub"]))
