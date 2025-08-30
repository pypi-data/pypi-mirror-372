from typing import Union


class RecursiveProcessor:
    """
    Base class for recursively processing nested data structures (dict, list, tuple, set).
    Override `process_leaf` to define how individual elements are handled.
    """

    def __init__(self, iterable_types=None):
        self.iterable_types = iterable_types or [list, tuple, set]

    def process_dict(self, d: dict):
        return {k: self.process(v) for k, v in d.items()}

    def process_sequence(self, seq: Union[list, tuple, set]):
        seq_type = type(seq)
        processed = [self.process(x) for x in seq]
        return seq_type(processed)

    def is_iterable_type(self, x):
        return any(isinstance(x, t) for t in self.iterable_types)

    def process_leaf(self, x):
        """Override in subclasses: define how to handle non-iterable elements."""
        raise NotImplementedError

    def process(self, x):
        if isinstance(x, dict):
            return self.process_dict(x)
        elif self.is_iterable_type(x):
            return self.process_sequence(x)
        return self.process_leaf(x)
