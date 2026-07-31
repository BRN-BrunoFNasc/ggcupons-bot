"""Testa a classificacao por nivel e a escolha do proximo da fila."""
import os, sys, tempfile
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import database, fila


def run():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False); db = tmp.name; tmp.close()
    database.init_db(db)
    agora = datetime.now(timezone.utc)

    def prod(pid, titulo, cupom=None, cd=None):
        database.add_product({"id": pid, "title": titulo, "permalink": "x", "thumbnail": None,
                              "affiliate_url": "x", "coupon_code": cupom, "coupon_note": None}, db)
        if cd:
            database.set_cooldown(pid, cd, db)

    # A: menor preco historico (cai hoje para o minimo)
    prod("A", "Placa de video")
    for i in range(10):
        database.record_price("A", 2500 - i * 10, 3000, db_path=db,
                              recorded_at=(agora - timedelta(days=10 - i)).isoformat())
    database.record_price("A", 1800, 3000, db_path=db, recorded_at=agora.isoformat())

    # B: tem cupom, desconto leve
    prod("B", "Headset gamer", cupom="GAMER10")
    database.record_price("B", 300, 330, db_path=db, recorded_at=agora.isoformat())

    # C: sem desconto (lancamento) com frequencia forcada de 15 min
    prod("C", "Lancamento novo", cd=15)
    database.record_price("C", 500, None, db_path=db, recorded_at=agora.isoformat())

    # D: desconto forte
    prod("D", "Monitor 144hz")
    database.record_price("D", 800, 1200, db_path=db, recorded_at=agora.isoformat())

    st = {x["id"]: x for x in fila.listar_status(db)}
    assert st["A"]["tier"] == "MENOR_PRECO", st["A"]["tier"]
    assert st["B"]["tier"] == "CUPOM", st["B"]["tier"]
    assert st["C"]["tier"] == "SEM_DESCONTO" and st["C"]["cooldown_min"] == 15
    assert st["D"]["tier"] == "DESCONTO_FORTE", st["D"]["tier"]

    # ordem de postagem agora e do rodizio (ver tests/test_rodizio.py).
    # aqui validamos: (1) todos comecam liberados, (2) apos postar entram em descanso.
    assert all(x["liberado"] for x in st.values()), "todos deveriam comecar liberados"

    escolhido = fila.proximo(db)
    assert escolhido is not None
    database.marcar_postado(escolhido["id"], escolhido["tier"], escolhido["preco"], db)
    depois = {x["id"]: x for x in fila.listar_status(db)}
    assert not depois[escolhido["id"]]["liberado"], "deveria estar em descanso apos postar"

    # prioridade = nivel * 100 + prioridade da categoria (nivel manda)
    assert st["A"]["prioridade"] > st["B"]["prioridade"] > st["D"]["prioridade"] > st["C"]["prioridade"]

    os.unlink(db)
    print("FILA OK ✅")
    print("  A=MENOR_PRECO  B=CUPOM  D=DESCONTO_FORTE  C=SEM_DESCONTO (freq forcada 15min)")
    print("  Niveis, prioridades e descanso corretos.")


if __name__ == "__main__":
    run()
