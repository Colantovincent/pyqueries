import datetime
import table

class Field:
    _SQL_TYPES = {
        "VARCHAR":  {
            "types": {str, int, float, type(None), datetime.datetime}
                    },
        "CHAR":     {
            "types": {str, int, float, type(None), datetime.datetime}
            },
        "TEXT":     {
            "types": {str, int, float, type(None), datetime.datetime}
            },
        "INT":      {
            "types": {str, int, float, type(None)}
            },
        "TINYINT":  {
            "types": {str, int, float, type(None)}
            },
        "BIGINT":   {
            "types": {str, int, float, type(None)}
            },
        "FLOAT":    {
            "types": {str, int, float, type(None)}
            },
        "DECIMAL":  {
            "types": {str, int, float, type(None)}
            },
        "DOUBLE":   {
            "types": {str, int, float, type(None)}
            },
        "DATETIME": {
            "types": {str, type(None), datetime.datetime}
            },
        "DATE":     {
            "types": {str, type(None), datetime.datetime}
            },
        "NULL":     {
            "types": {type(None)}
            }
    }

    def __init__(self,  name: str, size: int = -1, sql_type: str = "", nullable: bool = False, table: table.Table | None = None):
        self.table = table
        self.name = name
        self.size = size
        found_type = sql_type.upper().strip()
        if found_type in self._SQL_TYPES:
            self.sql_type = found_type
            self.sql_rules = self._SQL_TYPES[found_type]
        else:
            self.sql_type = ""
        self.nullable = nullable
    
    def __str__(self):
        return self.name
    
    def __lt__(self, other):
        self._validate_value(str(other))
        if self.table:
            stringified = f"`{self.table}`.`{self.name}` < {self.to_sql_format(other)}"
        else:
            stringified = f"`{self.name}` < {self.to_sql_format(other)}"
        return stringified
    def __gt__(self, other):
        self._validate_value(str(other))
        if self.table:
            stringified = f"`{self.table}`.`{self.name}` > {self.to_sql_format(other)}"
        else:
            stringified = f"`{self.name}` > {self.to_sql_format(other)}"
        return stringified
    def __eq__(self, other):
        self._validate_value(str(other))
        if self.table:
            stringified = f"`{self.table}`.`{self.name}` = {self.to_sql_format(other)}"
        else:
            stringified = f"`{self.name}` = {self.to_sql_format(other)}"
        return stringified
    def __ne__(self, other):
        self._validate_value(str(other))
        if self.table:
            stringified = f"`{self.table}`.`{self.name}` != {self.to_sql_format(other)}"
        else:
            stringified = f"`{self.name}` != {self.to_sql_format(other)}"
        return stringified
    def __le__(self, other):
        self._validate_value(str(other))
        if self.table:
            stringified = f"`{self.table}`.`{self.name}` <= {self.to_sql_format(other)}"
        else:
            stringified = f"`{self.name}` <= {self.to_sql_format(other)}"
        return stringified
    def __ge__(self, other):
        self._validate_value(str(other))
        if self.table:
            stringified = f"`{self.table}`.`{self.name}` >= {self.to_sql_format(other)}"
        else:
            stringified = f"`{self.name}` >= {self.to_sql_format(other)}"
        return stringified
    
    def _validate_value(self, val):
        if val is None:
            if not self.nullable:
                raise ValueError(f"Field '{self.name}' cannot be NULL")
            return
    
        length = len(val)
        val_type = type(val)

        if self.sql_type:
            if val_type not in self.sql_rules["types"]:
                raise TypeError(f"'{val}' ({val_type}) can't be converted to {self.sql_type} ({self.sql_rules})")
            
        if self.size > 0 and length > self.size:
            raise ValueError(f"Value '{val}' exceeds maximum length of field '{self.name}'\n'{val}': \t{length}\nmaximum: \t{self.size}")
        
    def to_sql_format(self, value):

        if isinstance(value, str):
            return f"'{value}'"
        elif value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return str(value)