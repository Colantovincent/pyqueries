import datetime
import table
import sqlpart

_PROHIBITED = {
        "`": "\\`",
        "'": "\\'",
        "\"": "\\\""
    }

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

    def __init__(self, name: str, size: int = -1, sql_type: str = "", nullable: bool = True, source_table: table.Table | None = None):
        self.source_table = source_table
        self.name = name
        self.size = size
        found_type = sql_type.upper().strip()
        if found_type in self._SQL_TYPES:
            self.sql_type = found_type
            self.sql_rules = self._SQL_TYPES[found_type]
        else:
            self.sql_type = None
        self.nullable = nullable
    
    def __str__(self):
        return self.name
    
    def __lt__(self, other):
        self._validate_value(other)
        if self.source_table:
            string_rep = sqlpart.SQLPart(f"`{self.source_table}`.`{self.name}` < %s", other)
        else:
            string_rep = sqlpart.SQLPart(f"`{self.name}` < %s", other)
        return string_rep
    def __gt__(self, other):
        self._validate_value(other)
        if self.source_table:
            string_rep = sqlpart.SQLPart(f"`{self.source_table}`.`{self.name}` > %s", other)
        else:
            string_rep = sqlpart.SQLPart(f"`{self.name}` > %s", other)
        return string_rep
    def __eq__(self, other):
        self._validate_value(other)

        if other is None:
            comparison = "IS"
        else:
            comparison = "="

        if self.source_table:
            string_rep = sqlpart.SQLPart(f"`{self.source_table}`.`{self.name}` {comparison} %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` {comparison} %s", other)
        
        return string_rep
    def __ne__(self, other):
        self._validate_value(other)

        if other is None:
            comparison = "IS NOT"
        else:
            comparison = "!="

        if self.source_table:
           string_rep = sqlpart.SQLPart(f"`{self.source_table}`.`{self.name}` {comparison} %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` {comparison} %s", other)
        return string_rep
    def __le__(self, other):
        self._validate_value(other)
        if self.source_table:
           string_rep = sqlpart.SQLPart(f"`{self.source_table}`.`{self.name}` <= %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` <= %s", other)
        return string_rep
    def __ge__(self, other):
        self._validate_value(other)
        if self.source_table:
           string_rep = sqlpart.SQLPart(f"`{self.source_table}`.`{self.name}` >= %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` >= %s", other)
        return string_rep
    
    def _validate_value(self, val):
        if val is None:
            if not self.nullable:
                raise ValueError(f"Field '{self.name}' cannot be NULL")
            return
    
        length = len(str(val))
        val_type = type(val)

        if self.sql_type:
            if val_type not in self.sql_rules["types"]:
                raise TypeError(f"'{val}' ({val_type}) can't be converted to {self.sql_type} ({self.sql_rules})")
            
        if 0 < self.size < length:
            raise ValueError(f"Value '{val}' exceeds maximum length of field '{self.name}'\n'{val}': \t{length}\nmaximum: \t{self.size}")