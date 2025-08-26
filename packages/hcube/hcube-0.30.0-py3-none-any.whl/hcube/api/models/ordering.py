from enum import Enum
from typing import Union

from hcube.api.models.aggregation import Aggregation
from hcube.api.models.dimensions import Dimension
from hcube.api.models.metrics import Metric


class OrderDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class OrderSpec:
    def __init__(
        self,
        dimension: Union[Dimension, Aggregation, Metric],
        direction: OrderDirection = OrderDirection.ASC,
    ):
        self.dimension = dimension
        self.direction = direction
