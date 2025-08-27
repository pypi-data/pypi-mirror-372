from abc import ABC, abstractmethod
from typing import Iterator, override
from .sweep_types import SweepRange


class PredictiveIterator(ABC, Iterator):
    @abstractmethod
    def has_next(self) -> bool: ...


class SweepRangeIterator(PredictiveIterator):
    """iterator for a range defined as SweepRange typed dict"""

    def __init__(self, sweep_range: SweepRange):
        self.sweep_range = sweep_range
        self.current = sweep_range['min']

    @override
    def __iter__(self):
        return self

    @override
    def __next__(self):
        if not self.has_next():
            raise StopIteration
        result = self.current
        self.current += self.sweep_range['step']
        return result

    def __len__(self):
        if self.sweep_range['max'] < self.sweep_range['min']:
            return 0
        return int((self.sweep_range['max'] - self.sweep_range['min']) / self.sweep_range['step']) + 1

    @override
    def has_next(self):
        """
        Check if end has been reached.
        This way we can avoid raising/handling the StopIteration exception
        """
        return self.current <= self.sweep_range['max']


class SweepMultiRangeIterator(PredictiveIterator):
    """iterator for multiple ranges defined as SweepRange typed dicts"""

    def __init__(self, sweep_ranges: list[SweepRange]):
        self.sweep_ranges = sweep_ranges
        self.range_iterators = [SweepRangeIterator(r) for r in sweep_ranges]
        self.end_reached = False
        for r in self.range_iterators:
            if not r.has_next():
                self.end_reached = True
                break
        if not self.end_reached:
            self.vector = [next(r) for r in self.range_iterators]

    def __len__(self):
        total = 1
        for r in self.range_iterators:
            total *= len(r)
        return total

    @override
    def __iter__(self):
        return self

    @override
    def __next__(self):
        """loop throw each iterator in a nested way exhausting all possible combinations"""
        if not self.has_next():
            raise StopIteration
        result = self.vector.copy()
        could_iterate = False
        for i, r in enumerate(self.range_iterators):
            if r.has_next():
                self.vector[i] = next(r)
                for j in range(i):
                    self.range_iterators[j] = SweepRangeIterator(self.sweep_ranges[j])
                    self.vector[j] = next(self.range_iterators[j])
                could_iterate = True
                break
        if not could_iterate:
            self.end_reached = True
        return result

    @override
    def has_next(self):
        return not self.end_reached
