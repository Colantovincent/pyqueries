import field
import table
import sqlpart
import typing

class Query:
    def __init__(self):
        self.string_representation = ""
        self.where_clauses = list[sqlpart.SQLPart]()
    
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
    
    def get_string(self) -> typing.Tuple[str, typing.List[typing.Any]]:
        sql = self.string_representation
        params: typing.List[typing.Any] = []
        if self.where_clauses:
            sql += "WHERE " + " AND ".join(p.sql for p in self.where_clauses)
            for p in self.where_clauses:
                params.append(p.param)
        sql += ";"
        return sql, params