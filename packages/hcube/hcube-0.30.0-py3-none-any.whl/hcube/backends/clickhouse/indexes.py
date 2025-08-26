from dataclasses import dataclass


@dataclass
class IndexDefinition:
    name: str
    type: str
    expression: str  # what will be indexed - typically a name of column, but may be more
    granularity: int = 1

    def definition(self) -> str:
        return (
            f"INDEX {self.name} ({self.expression}) TYPE {self.type} GRANULARITY {self.granularity}"
        )
