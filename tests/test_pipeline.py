"""Teste offline: historico -> summary -> info -> caption + card, sem rede."""
import os, sys, tempfile
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import database, analytics, message, imagem


def run():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False); db = tmp.name; tmp.close()
    # isola o teste: o banco padrao passa a ser o temporario
    database.DB_PATH = db
    database.init_db(db)
    pid = "MLB_TESTE"
    database.add_product({"id": pid, "title": "Placa de Video RTX 4060",
                          "permalink": "https://ml/x", "thumbnail": None,
                          "affiliate_url": "https://meli.la/abc",
                          "coupon_code": "GAMER10", "coupon_note": "min R$100"}, db)
    base = datetime.now(timezone.utc) - timedelta(days=40)
    precos = [2499,2450,2380,2299,2420,2350,2280,2200,2320,2260]*4
    for i,pr in enumerate(precos):
        database.record_price(pid, pr, 2699, db_path=db, recorded_at=(base+timedelta(days=i)).isoformat())
    database.record_price(pid, 1999.0, 2699, db_path=db, recorded_at=datetime.now(timezone.utc).isoformat())

    summary = analytics.summarize(database.get_price_history(pid, db), windows=(30,60,90))
    assert summary["enough_history"] and summary["is_lowest_window"] >= 30
    product = database.get_products(db_path=db)[0]
    rd = {"title": product["title"], "price": 1999.0, "original_price": 2699.0,
          "parcelas": "10x R$ 199 sem juros", "frete": True, "thumbnail": None}
    info = message.build_info(product, rd, summary)
    cap = message.caption(info)
    assert "1.999,00" in cap and "GAMER10" in cap and "OFF" in cap and "Menor preço" in cap
    imagem.gerar_card({"title": info["title"], "thumbnail": None}, info, "/tmp/card_test.png")
    os.unlink(db)
    print("TODOS OS TESTES PASSARAM ✅\n")
    print(cap)


if __name__ == "__main__":
    run()
