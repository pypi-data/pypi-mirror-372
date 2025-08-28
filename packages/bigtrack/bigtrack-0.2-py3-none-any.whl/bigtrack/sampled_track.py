#!/usr/bin/env python3

import copy
import random
from .composite_track import CompositeTrack


class SampledCompositeTrack(CompositeTrack):

    def __init__(self, full_track: CompositeTrack, number: int, random_seed: int = 0, suffix: str = "_subset", **kwargs):

        super().__init__(**full_track.kwargs)
        self.parent = full_track.parent

        # update track identifier to avoid conflicts
        self.kwargs["track"] = self.kwargs["track"] + suffix
        random.seed(random_seed)
        for child in random.sample(full_track.children, k=number):
            child_copy = copy.deepcopy(child)
            child_copy.kwargs["track"] = child_copy.kwargs["track"] + suffix
            self.add_child(child_copy)

        # update remaining new args
        for k, v in kwargs.items():
            self.kwargs[k] = v
