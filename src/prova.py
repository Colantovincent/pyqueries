import field

class Table:
    fields = []
 
class Query:
    def __init__(self):
        self.string_representation = ""
        self.where_clauses = []
    
    def select(self, fields: list, table: str):
        self.string_representation = "SELECT "

        if fields:
            for field in fields:
                self.string_representation += f"{field}, "
        else:
            self.string_representation += "* "

        self.string_representation += f"FROM {table} "

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
    nome = field.Field("nome", 3)
    print(field.Field._SQL_TYPES.get("VARCHAR"))
    myQuery.select([], "persona").where(nome == "mario")
  
    pprint.pprint(myQuery.get_string())