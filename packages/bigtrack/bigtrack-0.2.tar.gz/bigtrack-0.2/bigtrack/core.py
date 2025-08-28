#!/usr/bin/env python3

import os
import tomllib
from .hub import Hub


class Core(object):

    def __init__(self, config_path):

        self.hub = None
        self.config = self.parse_config_file(config_path)
        self.parse_config()
    
    def parse_config_file(self, path):

        suffix = os.path.splitext(path)[1].lower()

        if suffix == ".toml":
            with open(path, "rb") as f:
                return tomllib.load(f)

        elif suffix == ".json":
            with open(path, "r") as f:
                return json.load(f)
        
        else:
            raise ValueError(f"Unsopported config file type: {suffix}.")
    
    def parse_config(self):

        genomes = list()
        groups = list()
        trackDbs = list()
        tracks = list()

        

