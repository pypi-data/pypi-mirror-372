#!/usr/bin/env python3

from .hub_component import HubComponent
from .track import Track


class Group(HubComponent):

    default_kwargs = {
        "priority": 1,
        "defaultIsClosed": 0,
    }
    required_keys = ["name", "label", "priority", "defaultIsClosed"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.tracks = []
    
    def add_track(self, track: Track):

        if not isinstance(track, Track):
            raise ValueError(f"Track must be an instance of Track, not {type(track)}.")

        self.tracks.append(track)
    
    def generate(self):

        pass

