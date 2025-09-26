class Table:
    def __init__(self, name, fields = []):
        self.name = name
        self.fields = fields

    def __str__(self):
        return self.name