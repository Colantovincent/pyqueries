import field
import table
import sqlpart
import typing
import enum

from src.sqlpart import SQLPart


class JoinTypes(enum.Enum):
    """
    A simple enum to store all the JOIN logic currently handled to build meaningful queries
    """
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class OnClauses(enum.Enum):
    """
    Possible logic gates for ON-clauses (might work on where...?)
    """
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class Join:
    """
    Class for the objects representing SQL "JOIN" statements. References table, type of join and all the related logic
    conditions.
    """

    def __init__(self, join_table: table.Table | str, join_type: JoinTypes = JoinTypes.INNER):
        """
        Builds a join object. It is used in queries and to chain multiple conditions to a single table.
        The created object also has a list of logical conditions to join the main table.
        :param join_table: The table to reference (e.g. "Employee" or table.Table("Employee")
        :param join_type: The kind of join to implement (e.g. JoinTypes.LEFT) defaults to an inner join.
        """
        self._table = join_table
        self._table_name = self._table.name if isinstance(self._table, table.Table) else self._table
        self.join_type = join_type
        self.conditions: list[tuple[SQLPart, OnClauses | None]] = []

    def on(self, condition: SQLPart, condition_type: OnClauses | None = None):
        """
        Appends a new (condition, "AND"/"OR") tuple to the Join object's condition field and returns the object for
        chaining. If the object's .conditions parameter is empty, ignores condition_type (meaning this is the first ON
        clause of the object).

        :param condition: The logical condition in SQLPart format (e.g. salary > 1000 person.id=employee.id).
            Should be made with Field() objects comparisons.
        :param condition_type: Which logical gate should be used in the query (currently, OnClauses.AND/OnClauses.OR)
        :return: The object to which it appended
        """
        if not self.conditions:
            self.conditions.append((condition, None))
        else:
            if condition_type is None:
                raise ValueError("Multiple conditions in a single join require a condition_type (AND/OR)")
            self.conditions.append((condition, condition_type))
        return self

    def get_table(self):
        """
        Fetches the SQL name of the table that has been used to create the Join object
        :return: The object's table's name
        """
        return self._table_name


class Query:
    """
    Allows to build string-representations of SQL queries (for now only SELECT)
    """
    def __init__(self):
        """
        Initializes a Query() object. Call .select() after this to start the process
        """
        self.string_representation = ""
        self._from_table = None
        self._joined_tables: typing.Dict[str, Join] = {}  #table name -> Join()
        self.where_clauses = list[sqlpart.SQLPart]()
        #defaults to -1 as a Jolly to say "ignore this clause"
        self.limit_records = -1
        self.limit_offset = -1
        self.order_by_cols: list[field.Field] = []

    def _build_join(self):
        """
        Helper. Creates a raw string from the items in _joined_tables. Used in the get_string method.
        :return: The string obtained after parsing all the JOIN conditions.
        """
        if not self._joined_tables:
            return ""

        joins = []

        for join_object in self._joined_tables.values():
            #Creates a string like "INNER/LEFT/RIGHT JOIN table_name"
            clause = f"{join_object.join_type.value} JOIN {join_object.get_table()}"

            #For each condition, appends it to the string like "AND/OR field=other_field" (or other logic operators)
            if join_object.conditions:
                conds = []
                for i, (condition, condition_type) in enumerate(join_object.conditions):
                    if i == 0:
                        conds.append(f"ON {condition.sql.replace("%s", str(condition.param))}")
                    else:
                        conds.append(f"{condition_type} {condition.sql.replace("%s", str(condition.param))}")
                clause += " " + " ".join(conds)

            joins.append(clause)
        return " " + " ".join(joins)

    def _build_order_by(self):
        """
        Helper. Creates a raw string for the ORDER BY clause. Used in the get_string method.
        :return: A string in the format ORDER BY Field().name, Field().name ... or ORDER BY str, str ...
        """
        if self.order_by_cols:
            order_fields = []
            for col in self.order_by_cols:
                if isinstance(col, field.Field) and col.source_table:
                    order_fields.append(f"`{col.source_table.name}`.`{col.name}`")
                else:
                    order_fields.append(f"`{col}`")
            return " ORDER BY " + ", ".join(order_fields)

        #If order_by_cols is empty, this query has no ordering.
        return ""

    def select(self, fields: list[field.Field | str] | None = None, from_table: table.Table | str | None = None):
        """
        Generates a string in the format "SELECT fields FROM from_table".
        :param fields: A list of fields to retrieve in the query (e.g. [name, salary, dept]) Can contain either Field()
            objects or strings.
        :param from_table: The table from which the SELECT statement should access the fields.
        :return:
        """
        self.string_representation = "SELECT "

        if fields:
            self.string_representation += ", ".join(f"{query_field}" for query_field in fields)
        else:
            self.string_representation += "* "

        if from_table:
            if from_table == fields[0].source_table:
                self.string_representation += f" FROM {from_table} "

        return self

    def join(self, joined_table: table.Table | str):
        """
        Creates a Join() object and returns it to handle complex queries including JOIN and ON statements.
        :param joined_table: the Table() object to reference in the Join() or a string representing its name.
        :return: the created Join() object to do an .on() statement on.
        """
        if joined_table not in self._joined_tables:
            new_join = Join(joined_table)
            self._joined_tables[joined_table.name] = new_join
            return new_join
        else:
            raise ValueError("You're trying to join the same table multiple times in the same query!")

    def where(self, cond: str | sqlpart.SQLPart | bool = False):
        """
        Adds a condition to the WHERE clause of the query. If it's the first call of the method for this object, the
        result would be "... WHERE cond ...", if multiple .where() method calls happen, it defaults to chaining them with
        AND (e.g. "... WHERE cond_of_first_call AND cond_of_second_call AND cond_of_third_call ...")
        :param cond: a SQLPart object containing a valid SQL condition. (e.g. salary > 1000). Can be easily generated
            by running comparisons on Field() objects. Can also be a string if the condition is too complex.
        :return: The Query object that called the method, for further chaining.
        """
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
        """
        Adds an ORDER BY clause to the query and returns the Query.
        :param columns: either a string representing a field name or Field() object. Can also be a list to order the
            resultset by multiple columns. (Reference MySQL docs)
        :return: The Query object that called the method, for further chaining.
        """
        if isinstance(columns, list):
            for column in columns:
                self.order_by_cols.append(column)
        else:
            self.order_by_cols.append(columns)

        return self

    def limit(self, amount: int, offset: int =-1):
        """
        Adds a LIMIT statement to the query (... LIMIT amount OFFSET offset)
        :param amount: How many records to return. Must be a positive integer.
        :param offset: The offset of the LIMIT clause (Reference MySQL docs for further context). Must be a positive
            integer.
        :return: The Query object that called the method, for further chaining.
        """
        if amount >= 0:
            self.limit_records = amount
        else:
            raise ValueError("Cannot SELECT ... LIMIT 'x' with x < 0")

        if offset >= 0:
            self.limit_offset = offset
        else:
            raise ValueError("Cannot SELECT ... LIMIT ... OFFSET 'y' with 'y' < 0")
        return self

    def get_string(self) -> typing.Tuple[str, list]:
        """
        Builds and parametrizes the SQL representation of the Query() object.
        :return: A tuple containing the escaped-string to pass to the MySQL cursor and a list of parameters for the
            cursor to consume.
        """
        sql: str = self.string_representation

        params: list = []

        #Build the join clause of the string
        join_clause = self._build_join()
        sql += join_clause

        #Build and sanitize WHERE clauses
        if self.where_clauses:
            sql += "WHERE " + " AND ".join(p.sql for p in self.where_clauses)
            for p in self.where_clauses:
                params.append(p.param)
            #Adding a trailing space for future statements
            sql += " "

        #Build ORDER BY and LIMIT clauses
        if self.order_by_cols:
            sql += "ORDER BY " + ", ".join(col.name for col in self.order_by_cols)

        sql += f"LIMIT {self.limit_records} " if self.limit_records > 0 else ""
        sql += f"OFFSET {self.limit_offset} " if self.limit_offset > 0 else ""

        sql = sql.strip() + ";"
        return sql, params
