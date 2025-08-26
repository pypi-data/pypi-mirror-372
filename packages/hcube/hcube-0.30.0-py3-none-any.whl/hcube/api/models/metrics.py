import abc
from typing import Any, Optional


class Metric(abc.ABC):  # noqa: B024
    """
    Metric stores a value for a specific cell in the cube.
    """

    _type: Optional[type] = None

    def __init__(self, name: Optional[str] = None, help_text: str = "", **kwargs):
        """
        Name could be supplied later on if the dimension is declared in HCube class specification
        for example.

        kwargs are passed to the backend and may be used to pass special arguments to individual
        backends
        """
        self.name: Optional[str] = name
        self.help_text = help_text
        self.kwargs = kwargs

    def to_python(self, value: Any):
        """
        Simple implementation that uses `self._type` for conversion. Child classes may completely
        override this method.
        """
        if not self._type:
            raise NotImplementedError("Dimension type is not specified")
        return self._type(value)


class IntMetric(Metric):
    _type = int

    def __init__(
        self,
        name: Optional[str] = None,
        signed: bool = True,
        bits: int = 32,
        help_text: str = "",
        **kwargs,
    ):
        """
        Backends are not required to use the `signed` and `bits` information. They are there just
        as hints to backends which support it.
        """
        super().__init__(name, help_text=help_text, **kwargs)
        self.signed = signed
        self.bits = bits


class FloatMetric(Metric):
    _type = float
