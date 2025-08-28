#!/usr/bin/env python3

from .track import Track


class CompositeTrack(Track):

    default_kwargs = {
        "compositeTrack": "on",
        "parent": None,
    }
    required_keys = ["track", "compositeTrack", "parent", "shortLabel", "longLabel", "type"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
