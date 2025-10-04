import datetime
import table
import sqlpart

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
        self.nullable = nullable

        found_type = sql_type.upper().strip()
        if found_type in self._SQL_TYPES:
            self.sql_type = found_type
            self.sql_rules = self._SQL_TYPES[found_type]
        else:
            self.sql_type = None

    def __str__(self):
        #If the source_table is defined, returns table.field_name. Do not add backtick to source_table because
        #casting a Table object to string already adds them
        if self.source_table:
            return f"{self.source_table}.`{self.name}`"
        return f"`{self.name}`"

    #----------------------------------BASIC COMPARISON----------------------------------
    #TODO use __str__ overload of Field() objects to better create the SQLPart string-representation in the f-string
    def __lt__(self, other):
        self._validate_value(other)
        if self.source_table:
            string_rep = sqlpart.SQLPart(f"{self.source_table}.`{self.name}` < %s", other)
        else:
            string_rep = sqlpart.SQLPart(f"`{self.name}` < %s", other)
        return string_rep
    def __gt__(self, other):
        self._validate_value(other)
        if self.source_table:
            string_rep = sqlpart.SQLPart(f"{self.source_table}.`{self.name}` > %s", other)
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
            string_rep = sqlpart.SQLPart(f"{self.source_table}.`{self.name}` {comparison} %s", other)
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
           string_rep = sqlpart.SQLPart(f"{self.source_table}.`{self.name}` {comparison} %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` {comparison} %s", other)
        return string_rep
    def __le__(self, other):
        self._validate_value(other)
        if self.source_table:
           string_rep = sqlpart.SQLPart(f"{self.source_table}.`{self.name}` <= %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` <= %s", other)
        return string_rep
    def __ge__(self, other):
        self._validate_value(other)
        if self.source_table:
           string_rep = sqlpart.SQLPart(f"{self.source_table}.`{self.name}` >= %s", other)
        else:
           string_rep = sqlpart.SQLPart(f"`{self.name}` >= %s", other)
        return string_rep

    #----------------------------------SQL-SPECIFIC OPERATIONS----------------------------------
    @staticmethod
    def between(self, minimum, maximum):
        """
        Handles the BETWEEN statement. Allows to generate statements like "... WHERE field BETWEEN minimum AND maximum"
        (refer to MySQL docs for further context)
        :param self: The field to use as the base.
        :param minimum: The minimum value for the between statement. Is going to be the first.
        :param maximum: The maximum value for the between statement. Is going to be the second.
        :return: A SQLPart object containing the parameterized statement and its values.
        """
        self._validate_value(minimum)
        self._validate_value(maximum)
        return sqlpart.SQLPart("BETWEEN %s AND %s", (minimum, maximum))

    def _validate_value(self, val):
        if val is None:
            if not self.nullable:
                raise ValueError(f"Field '{self.name}' cannot be NULL")
            return

        if isinstance(val, Field):
            if self.sql_type:
                if self.sql_type == val.sql_type:
                    return
                else:
                    raise TypeError(f"Can't compare '{val}' ({val.sql_type}) due to type mismatch with {self.sql_type}")

        length = len(str(val))
        val_type = type(val)

        if self.sql_type:
            if val_type not in self.sql_rules["types"]:
                raise TypeError(f"'{val}' ({val_type}) can't be converted to {self.sql_type} ({self.sql_rules})")
            
        if 0 < self.size < length:
            raise ValueError(f"Value '{val}' exceeds maximum length of field '{self.name}'\n'{val}': \t{length}\nmaximum: \t{self.size}")