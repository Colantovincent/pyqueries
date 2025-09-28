import field
import table

class Query:
    def __init__(self):
        self.string_representation = ""
        self.where_clauses = list[str | bool]()
    
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

    def where(self, cond: str | bool = False):
        if cond:
            self.where_clauses.append(cond)

        return self
    
    def get_string(self):
        string = self.string_representation
        
        if self.where_clauses:
            string += "WHERE " + str.join(" AND ", self.where_clauses)

        string += ";"
        return string