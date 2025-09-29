from dataclasses import dataclass
import typing
@dataclass
class SQLPart:
    sql: str
    param: typing.Any