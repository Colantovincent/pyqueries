import field
import table

class Query:
    def __init__(self):
        self.string_representation = ""
        self.where_clauses = []
    
    def select(self, fields: list[field.Field, str], table: str):
        self.string_representation = "SELECT "

        if fields:
            for field in fields:
                self.string_representation += f"`{field}`, "
        else:
            self.string_representation += "* "

        if table:
            if table == fields[0].table:
                self.string_representation += f"FROM `{table}` "

        return self

    def where(self, cond = False):
        if cond:
            self.where_clauses.append(cond)

        return self
    
    def get_string(self):
        string = self.string_representation
        
        if self.where_clauses:
            string += "WHERE " + str.join(" AND ", self.where_clauses)
        
        return string
    

if __name__ == "__main__":
    import pprint

    myQuery = Query()

    persona = table.Table("persona" )
    nome = field.Field("nome", 45, "VARCHAR", False, persona)
    myQuery.select([nome], persona).where(nome == "Mario' AND 1=1")
    
    pprint.pprint(myQuery.get_string())