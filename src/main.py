from prova import Query
import table

if __name__ == "__main__":

    myQuery = Query()

    persona = table.Table("persona")
    nome = persona.register_field("nome", **{"size": 45, "sql_type": "VARCHAR", "nullable": True})
    eta = persona.register_field("eta", **{"size": 3, "sql_type": "INT", "nullable": True})
    myQuery.select([persona.fields["nome"]], persona).where(persona.fields["nome"] == "`Mario\"' AND 1 = 1").where(persona.fields["eta"] != 1).where(eta > 0)

    print(myQuery.get_string())