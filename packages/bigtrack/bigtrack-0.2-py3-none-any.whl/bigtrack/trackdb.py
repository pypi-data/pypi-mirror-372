#!/usr/bin/env python3

import os
from .hub_component import HubComponent
from .track import Track


class TrackDb(HubComponent):

    required_keys = ["include"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.tracks = []
    
    def add_track(self, track: Track):

        if not isinstance(track, Track):
            raise ValueError(f"Track must be an instance of Track, not {type(track)}.")

        self.tracks.append(track)
    
    def generate(self, target_path=""):

        with open(os.path.join(target_path, self.kwargs["include"]), "w") as tracks_f:
            for track in self.tracks:
                tracks_f.write(track.format(indent_level=0))
                track.generate(tracks_f)

