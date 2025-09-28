import field
class Table:
    def __init__(self, name: str, fields: dict | None = None):
        if fields is None:
            fields = dict()
        self.name = name
        self.fields = fields

    def register_field(self, name: str, **kwargs):
        new_field = field.Field(name=name, source_table=self, **kwargs)
        self.fields[name] = new_field
        return new_field

    def __str__(self):
        return self.name