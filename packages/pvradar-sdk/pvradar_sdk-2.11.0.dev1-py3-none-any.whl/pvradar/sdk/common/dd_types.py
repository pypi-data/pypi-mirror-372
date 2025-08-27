from dataclasses import dataclass
from typing import Literal, Optional, runtime_checkable
from typing import Protocol

DDPeriodType = Literal[
    'eternity',
    'year',
    'year-range',
    'year-list',
    'month-range',
    'month-list',
    'date-range',
    'date-list',
    'timestamps',
]


@dataclass
class DDPeriod:
    period_type: DDPeriodType

    # unix timestamp or year. For months YYYYMM format is used'
    start: Optional[int] = None

    # unix timestamp or year. For months YYYYMM format is used
    end: Optional[int] = None

    # if year-list, date-list etc. Examples: [200201,200203], [20020101,20020102,20020104], [2005,2007]
    values: Optional[list[int]] = None


@runtime_checkable
class DDPeriodLike(Protocol):
    def to_DDPeriod(self) -> DDPeriod: ...


@dataclass
class DDLocation:
    lat: float
    lon: float
    alt: Optional[float] = None
