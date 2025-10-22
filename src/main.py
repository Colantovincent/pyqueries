from query import Query
import table

if __name__ == "__main__":
    """Situazione tipo: abbiamo una tabella "Persona" con i suoi campi e una tabella ordini con i suoi campi.
    Vogliamo trovare tutti gli utenti (tranne quelli chiamati mario per qualsivoglia ragione) che hanno acquistato un prodotto, aventi
    età compresa tra 0 e 14 anni, magari per applicargli uno sconto più in là. Ci interessa sapere l'età degli utenti, cosa hanno ordinato e il loro nome
    """
    myQuery = Query()

    persona = table.Table("persona")
    ordini = table.Table("ordini")
    
    idpersona = persona.register_field("id", **{"size": 3, "sql_type": "InT", "nullable": False})
    nome = persona.register_field("nome", **{"size": 45, "sql_type": "VARCHAR", "nullable": True})
    eta = persona.register_field("eta", **{"size": 3, "sql_type": "INT", "nullable": True})

    fk_persona = ordini.register_field("persona_id", size=3, sql_type="INT", nullable=False)
    oggetto_ordinato = ordini.register_field("nome_oggetto", size=20, sql_type="VARCHAR", nullable=True)
    (myQuery
     .select([nome, eta], persona)
     .where(nome != "Mario")
        .where(eta.between(0, 14))
        .where(eta != None)
     .order_by(eta)
     .join(ordini)
        .on(fk_persona == idpersona))

    sql, params = myQuery.get_string()
    print("Query:\t", sql, "\nParams:\t", params)