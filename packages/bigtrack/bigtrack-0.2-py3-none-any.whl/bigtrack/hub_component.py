#!/usr/bin/env python3


class HubComponent(object):

    default_kwargs = {}
    required_keys = []

    def __init__(self, **kwargs):

        self.kwargs = kwargs
        self._auto_complete_kwargs()
        self._validate_kwargs()
    
    def _print_kwargs(self, indent_level=0):

        s = []

        for k in self.required_keys:
            if k.startswith("_"): continue
            s.append(indent_level * 4 * " " + f"{k} {self.kwargs[k]}")
        
        for k, v in self.kwargs.items():
            if k.startswith("_"): continue
            if k not in self.required_keys:
                s.append(indent_level * 4 * " " + f"{k} {v}")

        return s

    def format(self, indent_level=0):

        s = self._print_kwargs(indent_level=indent_level)
        s.append("")
        return "\n".join(s) + "\n"

    def _auto_complete_kwargs(self):

        for k, v in self.default_kwargs.items():
            if k not in self.kwargs:
                self.kwargs[k] = v
    
    def _validate_kwargs(self):

        for k in self.required_keys:
            if k not in self.kwargs:
                raise ValueError(f"{self.__class__.__name__}: required key {k} not found in kwargs.")
    
    def generate(self, target_path=""):

        raise NotImplementedError(f"{self.__class__.__name__}: subclasses must implement their own _generate() method.")
