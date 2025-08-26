import abc
import ipaddress
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Optional, Type, Union

if TYPE_CHECKING:
    from hcube.api.models.cube import Cube


class Dimension(abc.ABC):  # noqa: B024
    """
    Dimensions define the actual axes of the data/cube.
    """

    _type: Optional[type] = None
    default = None

    def __init__(
        self,
        name: Optional[str] = None,
        null: bool = False,
        help_text: str = "",
        **kwargs,
    ):
        """
        Name could be supplied later on if the dimension is declared in HCube class specification
        for example.

        :param name: Name of the dimension
        :param null: Whether the dimension can have null values
        :param help_text: Help text for the dimension
        :param kwargs: Additional keyword arguments - may be used to pass special arguments to
        individual backends
        """
        self.name: Optional[str] = name
        self.null = null
        self.help_text = help_text
        self.kwargs = kwargs
        self.cube: Optional[Type[Cube]] = None

    def __str__(self):
        cube_name = self.cube.__name__ if self.cube else "UnknownCube"
        return f"{cube_name}.{self.name}"

    def to_python(self, value: Any):
        """
        Simple implementation that uses `self._type` for conversion. Child classes may completely
        override this method.
        """
        if not self._type:
            raise NotImplementedError("Dimension type is not specified")
        self._check_null(value)
        if value is None:
            return value
        if isinstance(value, self._type):
            return value
        return self._type(value)

    def _check_null(self, value):
        if value is None and not self.null:
            raise ValueError(
                f"Dimension '{self.name}': "
                f"Null value is only allowed if the dimension has null=True"
            )


class StringDimension(Dimension):
    _type = str
    default = ""


class BooleanDimension(Dimension):
    _type = bool
    default = False


class IntDimension(Dimension):
    _type = int
    default = 0

    def __init__(
        self,
        name: Optional[str] = None,
        null: bool = False,
        signed: bool = True,
        bits: int = 32,
        help_text: str = "",
        **kwargs,
    ):
        """
        Backends are not required to use the `signed` and `bits` information. They are there just
        as hints to backends which support it.
        """
        super().__init__(name, null, help_text=help_text, **kwargs)
        self.signed = signed
        self.bits = bits


class DateDimension(Dimension):
    _type = date
    default = date(1970, 1, 1)

    def to_python(self, value: Union[str, date, datetime]):
        self._check_null(value)
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        return date.fromisoformat(value)


class DateTimeDimension(Dimension):
    _type = datetime
    default = datetime(1970, 1, 1, 0, 0, 0)

    def to_python(self, value: Union[str, date, datetime]):
        self._check_null(value)
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        return datetime.fromisoformat(value)


class ArrayDimension(Dimension):
    _type = list
    default = []

    def __init__(
        self,
        name: Optional[str] = None,
        null: bool = False,
        dimension: Dimension = None,
        help_text: str = "",
        **kwargs,
    ):
        super().__init__(name, null=null, help_text=help_text, **kwargs)
        self.dimension = dimension


class MapDimension(Dimension):
    _type = dict
    default = {}

    def __init__(
        self,
        name: Optional[str] = None,
        null: bool = False,
        key_dimension: Dimension = None,
        value_dimension: Dimension = None,
        help_text: str = "",
        **kwargs,
    ):
        super().__init__(name, null=null, help_text=help_text, **kwargs)
        self.key_dimension = key_dimension
        self.value_dimension = value_dimension


class IPDimension(Dimension):
    """Base for IP address dimensions"""

    _type = None
    default = ""

    def to_python(self, value: Any):
        self._check_null(value)
        if value is None:
            return value
        if not value:
            return self._type(self.default)
        return self._type(value)


class IPv4Dimension(IPDimension):
    _type = ipaddress.IPv4Address
    default = "0.0.0.0"


class IPv6Dimension(IPDimension):
    _type = ipaddress.IPv6Address
    default = "::"
