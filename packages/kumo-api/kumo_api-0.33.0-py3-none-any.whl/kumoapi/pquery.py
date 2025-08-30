from typing import Optional

from pydantic.dataclasses import dataclass

from kumoapi.common import StrEnum
from kumoapi.graph import GraphDefinition


@dataclass
class PQueryResource:
    """Predictive Query resource definition."""
    query_string: str
    graph: GraphDefinition
    name: Optional[str] = None
    desc: Optional[str] = ''


class QueryType(StrEnum):
    r"""Defines the type of a predictive query."""
    STATIC = 'static'
    TEMPORAL = 'temporal'
