"""Interfaces for CSV data stuff."""


def attr_list(cls):
    """Return list of attributes values for class."""
    return [val for key, val in vars(cls).items() if not key.startswith('_')]


class Error(Exception):
    """Package exception."""


class ObjectClass:
    """Classes of csv objects."""

    WELD = 0
    MARKER = 1
    DEFEKT = 2
    THICK = 3
    HOR_WELD = 4
    PIPELINE_CATEGORY = 5
    DIAM = 6


class TypeHorWeld:
    """Types of horizontal weld."""

    HORIZONTAL = 0
    SECOND = 1
    NO_WELD = 2
    SPIRAL = 3
    UNKNOWN = 4


class DefektSide:
    """Types of defekt location."""

    UNKNOWN = 0
    OUTSIDE = 1
    INSIDE = 2
    IN_WALL = 3
