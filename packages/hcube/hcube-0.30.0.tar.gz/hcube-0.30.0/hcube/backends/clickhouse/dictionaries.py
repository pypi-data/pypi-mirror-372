import hashlib
import json
from dataclasses import dataclass
from typing import Optional

from hcube.api.models.cube import Cube
from hcube.api.models.dimensions import IntDimension, StringDimension
from hcube.backends.clickhouse.data_sources import DataSource


@dataclass
class DictionaryAttr:
    name: str
    type: str
    expression: Optional[str] = None
    null_value: str = "NULL"
    injective: bool = False

    def definition_sql(self):
        expression = f"EXPRESSION {self.expression}" if self.expression else ""
        default = f"DEFAULT {self.null_value}" if self.null_value else ""
        type_part = f"Nullable({self.type})" if self.null_value == "NULL" else self.type
        return (
            f"{self.name} {type_part} {default} {expression} "
            f"{'INJECTIVE' if self.injective else ''}"
        )


class DictionaryDefinition:
    def __init__(
        self,
        name: str,
        source: DataSource,
        key: str,
        layout: str,
        attrs: [DictionaryAttr],
        lifetime_min: int = 600,
        lifetime_max: int = 720,
    ):
        self.name = name
        self.key = key
        self.source = source
        self.layout = layout
        self.attrs = attrs
        self.lifetime_min = lifetime_min
        self.lifetime_max = lifetime_max

    def definition_sql(self, database=None):
        db_part = f"{database}." if database else ""
        attrs = ",\n".join([attr.definition_sql() for attr in self.attrs])
        return (
            f"CREATE DICTIONARY IF NOT EXISTS {db_part}{self.name} ("
            f"{self.key} UInt64,\n"
            f"{attrs}"
            f") "
            f"PRIMARY KEY {self.key} "
            f"{self.source.definition_sql()} "
            f"LAYOUT ({self.layout.upper()}()) "
            f"LIFETIME(MIN {self.lifetime_min} MAX {self.lifetime_max}) "
            f"COMMENT 'blake2:{self.checksum}'"
        )

    @property
    def checksum(self):
        data = {
            "name": self.name,
            "key": self.key,
            "source": self.source.definition_sql(),
            "layout": self.layout,
            "attrs": [attr.definition_sql() for attr in self.attrs],
            "lifetime_min": self.lifetime_min,
            "lifetime_max": self.lifetime_max,
        }
        return hashlib.blake2b(json.dumps(data).encode("utf-8"), digest_size=32).hexdigest()

    def drop_sql(self, database=None):
        db_part = f"{database}." if database else ""
        return f"DROP DICTIONARY IF EXISTS {db_part}{self.name} SYNC"

    def create_cube(self) -> Cube:
        class Out(Cube):
            class Clickhouse:
                source = self

        for attr in self.attrs:
            setattr(Out, self.key, IntDimension())
            setattr(Out, attr.name, StringDimension())

        Out._process_attrs()
        return Out
