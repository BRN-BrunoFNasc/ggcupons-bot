"""Verifica que o rodizio alterna categorias e que a queda de preco fura a fila."""
import os, sys, tempfile
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import database, fila


def run():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False); db = tmp.name; tmp.close()
    database.init_db(db)
    agora = datetime.now(timezone.utc).isoformat()

    catalogo = [("Jogos", 4), ("Consoles", 4), ("Controles", 4),
                ("Acessorios Gamer", 3), ("Monitores", 3), ("Fones", 2), ("Gift Card", 2)]
    for cat, qtd in catalogo:
        for n in range(qtd):
            pid = f"{cat[:3].upper()}{n}"
            database.add_product({"id": pid, "title": f"{cat} item {n}", "permalink": "x",
                                  "thumbnail": None, "affiliate_url": "x",
                                  "coupon_code": None, "coupon_note": None,
                                  "categoria": cat}, db)
            database.record_price(pid, 500 - n * 10, 800, db_path=db, recorded_at=agora)

    print("Sequencia de postagem (rodizio):")
    seq = []
    for i in range(10):
        p = fila.proximo(db)
        if not p:
            print("  (fila vazia)"); break
        seq.append(p["categoria"])
        print(f"  {i+1:>2}. {p['categoria']:<18} {p['id']:<8} {p.get('motivo','')}")
        database.marcar_postado(p["id"], p["tier"], p["preco"], db)

    repetidos = [i for i in range(1, len(seq)) if seq[i] == seq[i-1]]
    assert not repetidos, f"categoria repetida em sequencia: {seq}"
    print("\n  -> nenhuma categoria repetida em sequencia ✅")

    # queda de preco num produto AINDA NAO postado: deve furar a fila
    database.marcar_urgente("MON1", 18.5, db)
    p = fila.proximo(db)
    assert p["id"] == "MON1" and p["urgente"], p
    print(f"  -> queda de preco furou a fila: {p['id']} ({p['motivo']}) ✅")

    # produto recem-postado NAO deve ser reposto na hora, mesmo com queda
    database.marcar_postado("MON1", "DESCONTO_FORTE", 400, db)
    database.marcar_urgente("MON1", 25.0, db)
    p2 = fila.proximo(db)
    assert p2["id"] != "MON1", "nao deveria repostar o mesmo item na sequencia"
    print(f"  -> respeitou o intervalo minimo do mesmo produto (escolheu {p2['id']}) ✅")

    os.unlink(db)
    print("\nRODIZIO OK ✅")


if __name__ == "__main__":
    run()
