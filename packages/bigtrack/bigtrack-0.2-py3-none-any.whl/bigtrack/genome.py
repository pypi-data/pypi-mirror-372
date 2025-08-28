#!/usr/bin/env python3

import os
from .hub_component import HubComponent
from .group import Group
from .trackdb import TrackDb


class Genome(HubComponent):

    default_kwargs = {
        "trackDb": "trackDb.txt",
        "groups": "groups.txt",
    }
    required_keys = ["genome", "trackDb", "groups", "organism", "scientificName"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.hub = None
        self.groups = []
        self.trackDbs = []
    
    def _auto_complete_kwargs(self):

        for k, v in self.default_kwargs.items():
            if k not in self.kwargs:
                if k in ["trackDb", "groups"]:
                    self.kwargs[k] = os.path.join(self.kwargs["genome"], v)
                else:
                    self.kwargs[k] = v
    
    def add_group(self, group: Group):

        if not isinstance(group, Group):
            raise ValueError(f"Group must be an instance of Group, not {type(group)}.")

        self.groups.append(group)
    
    def add_trackDb(self, trackDb: TrackDb):

        if not isinstance(trackDb, TrackDb):
            raise ValueError(f"TrackDb must be an instance of TrackDb, not {type(trackDb)}.")
        
        self.trackDbs.append(trackDb)

    def generate(self, target_path=""):

        os.makedirs(os.path.join(target_path, self.kwargs["genome"]), exist_ok=True)

        # generate groups.txt
        with open(os.path.join(target_path, self.kwargs["groups"]), "w") as groups_f:
            for group in self.groups:
                groups_f.write(group.format())
        
        # generate trackDb.txt
        with open(os.path.join(target_path, self.kwargs["trackDb"]), "w") as trackDb_f:
            for trackDb in self.trackDbs:
                trackDb_f.write(trackDb.format())
                trackDb.generate(os.path.join(target_path, self.kwargs["genome"]))
