#!/usr/bin/env python3

from .hub_component import HubComponent


class Track(HubComponent):

    default_kwargs = {
        "parent": None,
    }
    required_keys = ["track", "parent", "shortLabel", "longLabel", "type"]

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.parent = None
        self.children = []
    
    def format(self, indent_level=0):

        s = self._print_kwargs(indent_level=indent_level)
        s.append("")
        if self.parent is None:
            del s[self.required_keys.index("parent")]
        return "\n".join(s) + "\n"
        
    def add_parent(self, parent: "Track"):

        self.parent = parent
        self.kwargs["parent"] = parent.kwargs["track"]
        parent.children.append(self)
    
    def add_child(self, child: "Track"):

        child.parent = self
        child.kwargs["parent"] = self.kwargs["track"]
        self.children.append(child)

    def generate(self, file_handle=None, indent_level=0):

        for child in self.children:
            file_handle.write(child.format(indent_level=indent_level+1))
            child.generate(file_handle, indent_level=indent_level+1)
