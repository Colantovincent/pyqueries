import field
import table
import sqlpart
import typing

class Query:
    def __init__(self):
        self.string_representation = ""
        self.where_clauses = list[sqlpart.SQLPart]()
        self.limit_records = -1
        self.limit_offset = -1
        self.order_by_cols = []
    
    def select(self, fields: list[field.Field | str] | None = None, from_table: table.Table | str | None = None):
        self.string_representation = "SELECT "

        if fields:
            self.string_representation += ", ".join(f"`{query_field}`" for query_field in fields)
        else:
            self.string_representation += "* "

        if from_table:
            if from_table == fields[0].source_table:
                self.string_representation += f" FROM `{from_table}` "

        return self

    def where(self, cond: str | sqlpart.SQLPart | bool = False):
        if not cond:
            return self
        if isinstance(cond, sqlpart.SQLPart):
            self.where_clauses.append(cond)
        elif isinstance(cond, str):
            # Accept raw string (advanced manual), with no params
            self.where_clauses.append(sqlpart.SQLPart(cond, []))
        else:
            raise TypeError("where() expects SQLPart or str (or falsy to skip).")
        return self

    def order_by(self, columns: field.Field | str | typing.List[field.Field | str]):
        if isinstance(columns, list):
            for column in columns:
                self.order_by_cols.append(column)
        else:
            self.order_by_cols.append(columns)

        return self

    def limit(self, amount, offset = -1):
        if amount >= 0:
            self.limit_records = amount
        else:
            raise ValueError("Cannot SELECT ... LIMIT 'x' with x < 0")

        if offset >= 0:
            self.limit_offset = offset
        else:
            raise ValueError("Cannot SELECT ... LIMIT ... OFFSET 'y' with 'y' < 0")

    def get_string(self) -> typing.Tuple[str, typing.List[typing.Any]]:
        sql: str = self.string_representation

        params: typing.List[typing.Any] = []
        if self.where_clauses:
            sql += "WHERE " + " AND ".join(p.sql for p in self.where_clauses)
            for p in self.where_clauses:
                params.append(p.param)
            #Adding a trailing space
            sql += " "
        if self.order_by_cols:
            sql += "ORDER BY " + ", ".join(col.name for col in self.order_by_cols)

        sql += f"LIMIT {self.limit_records} " if self.limit_records > 0 else ""
        sql += f"OFFSET {self.limit_offset} " if self.limit_offset > 0 else ""

        sql = sql.strip() + ";"
        return sql, params