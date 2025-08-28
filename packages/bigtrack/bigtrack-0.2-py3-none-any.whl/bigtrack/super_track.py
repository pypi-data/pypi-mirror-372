#!/usr/bin/env python3

from .track import Track


class SuperTrack(Track):

    default_kwargs = {
        "superTrack": "on",
        "parent": None,
    }
    required_keys = ["track", "superTrack", "parent", "shortLabel", "longLabel"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
