from datetime import datetime
from typing import override

from ..common.dd_types import DDPeriod


class Period:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    @override
    def __str__(self):
        return f'{self.start} - {self.end}'

    @override
    def __repr__(self):
        return f'{self.start} - {self.end}'

    @override
    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    @override
    def __hash__(self):
        return hash((self.start, self.end))

    def __contains__(self, item):
        return self.start <= item <= self.end

    def __sub__(self, other):
        if self.start < other.start:
            return Period(self.start, other.start)
        else:
            return Period(other.end, self.end)

    def __add__(self, other):
        return Period(self.start, other.end)

    def __lt__(self, other):
        return self.start < other.start

    def __gt__(self, other):
        return self.start > other.start

    def __le__(self, other):
        return self.start <= other.start

    def __ge__(self, other):
        return self.start >= other.start

    @override
    def __ne__(self, other):
        return self.start != other.start or self.end != other.end

    def __len__(self):
        return (self.end - self.start).days

    def __iter__(self):
        return iter([self.start, self.end])

    def __getitem__(self, item):
        return [self.start, self.end][item]

    def __bool__(self):
        return self.start != self.end

    def contains(self, other):
        return self.start <= other.start and self.end >= other.end

    def to_DDPeriod(self) -> DDPeriod:
        return DDPeriod(
            period_type='year-range',
            start=int(self.start.year),
            end=int(self.end.year),
        )

    @classmethod
    def year_range(cls, start_year: int, end_year: int):
        return cls(
            start=datetime(start_year, 1, 1),
            end=datetime(end_year, 12, 31, 23, 59, 59),
        )
