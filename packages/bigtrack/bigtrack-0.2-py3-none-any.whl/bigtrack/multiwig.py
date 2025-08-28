#!/usr/bin/env python3

from .track import Track


class MultiWig(Track):

    default_kwargs = {
        "parent": None,
        "container": "multiWig",
        "type": "bigWig",
    }
    required_keys = ["track", "parent", "container", "type", "shortLabel", "longLabel"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
