import datetime
import table
import sqlpart

class Field:
    _SQL_TYPES = {
        "VARCHAR":  {"types": {str, int, float, type(None), datetime.datetime}},
        "CHAR":     {"types": {str, int, float, type(None), datetime.datetime}},
        "TEXT":     {"types": {str, int, float, type(None), datetime.datetime}},
        "INT":      {"types": {str, int, float, type(None)}},
        "TINYINT":  {"types": {str, int, float, type(None)}},
        "BIGINT":   {"types": {str, int, float, type(None)}},
        "FLOAT":    {"types": {str, int, float, type(None)}},
        "DECIMAL":  {"types": {str, int, float, type(None)}},
        "DOUBLE":   {"types": {str, int, float, type(None)}},
        "DATETIME": {"types": {str, type(None), datetime.datetime}},
        "DATE":     {"types": {str, type(None), datetime.datetime}},
        "NULL":     {"types": {type(None)}},
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
            self.sql_rules = None

    def __str__(self):
        #If the source_table is defined, returns `table`.`field`. Table.__str__ already adds backticks.
        if self.source_table:
            return f"{self.source_table}.`{self.name}`"
        return f"`{self.name}`"

    # ------------------------------- BASIC COMPARISONS --------------------------------
    def __lt__(self, other):  return self._cmp("<", other)
    def __le__(self, other):  return self._cmp("<=", other)
    def __gt__(self, other):  return self._cmp(">", other)
    def __ge__(self, other):  return self._cmp(">=", other)
    def __eq__(self, other):  return self._cmp("=", other)
    def __ne__(self, other):  return self._cmp("!=", other)

    # --------------------------- SQL-SPECIFIC OPERATIONS ------------------------------
    def between(self, minimum, maximum):
        """
        Generate: <field> BETWEEN %s AND %s
        """
        self._validate_value(minimum)
        self._validate_value(maximum)
        return sqlpart.SQLPart(f"{self} BETWEEN %s AND %s", (minimum, maximum))

    # ------------------------------ INTERNAL HELPERS ---------------------------------
    def _cmp(self, op: str, other):
        """
        Centralized comparison builder that:
        - uses __str__ for identifiers
        - validates values/types
        - special-cases None and Field
        """
        self._validate_value(other)

        #NULL handling
        if other is None:
            if op in ("=", "=="):
                return sqlpart.SQLPart(f"{self} IS NULL", None)
            if op in ("!=", "<>"):
                return sqlpart.SQLPart(f"{self} IS NOT NULL", None)
            #For ops like <, <=, >, >= with NULL, MySQL returns NULL (unknown), which is rarely desired.
            #Raise to nudge the caller to use IS [NOT] NULL explicitly.
            raise ValueError(f"Cannot use operator '{op}' with NULL for field {self}")

        #Field-to-Field comparison -> identifier on RHS, no bound param
        if isinstance(other, Field):
            # Type-checked in _validate_value already
            return sqlpart.SQLPart(f"{self} {self._normalize_op(op)} {other}", None)

        #Simple value -> parameterized
        return sqlpart.SQLPart(f"{self} {self._normalize_op(op)} %s", other)

    @staticmethod
    def _normalize_op(op: str) -> str:
        # Clean up python-style equality and alt not-equal
        if op == "==":
            return "="
        if op == "<>":
            return "!="
        return op

    def _validate_value(self, val):
        if val is None:
            if not self.nullable:
                raise ValueError(f"Field '{self.name}' cannot be NULL")
            return

        if isinstance(val, Field):
            if self.sql_type and val.sql_type:
                if self.sql_type != val.sql_type:
                    raise TypeError(
                        f"Can't compare '{val}' ({val.sql_type}) due to type mismatch with {self.sql_type}"
                    )
            return  #fields compared by identifier, not by value size/type limits

        length = len(str(val))
        val_type = type(val)

        if self.sql_type and self.sql_rules:
            if val_type not in self.sql_rules["types"]:
                raise TypeError(f"'{val}' ({val_type}) can't be converted to {self.sql_type} ({self.sql_rules})")

        if 0 < self.size < length:
            raise ValueError(
                f"Value '{val}' exceeds maximum length of field '{self.name}'\n'{val}': \t{length}\nmaximum: \t{self.size}"
            )