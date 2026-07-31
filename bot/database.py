"""Banco de historico de preco (SQLite). Sem dependencias externas."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from bot.config import DB_PATH


def _conn(db_path=None):
    path = Path(db_path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    # timeout evita travar quando o loop esta escrevendo; WAL permite ler e
    # escrever ao mesmo tempo (painel + run_loop no mesmo banco)
    con = sqlite3.connect(path, timeout=15)
    con.row_factory = sqlite3.Row
    try:
        # espera ate 15s se outro processo (run_loop) estiver escrevendo,
        # em vez de falhar na hora.
        con.execute("PRAGMA busy_timeout=15000")
        # garante modo de journal classico (WAL quebra em pasta sincronizada)
        modo = con.execute("PRAGMA journal_mode").fetchone()[0]
        if str(modo).lower() == "wal":
            con.execute("PRAGMA journal_mode=DELETE")
    except Exception:
        pass
    return con


def init_db(db_path=None):
    con = _conn(db_path)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id            TEXT PRIMARY KEY,   -- MLB123... (id do anuncio)
            title         TEXT,
            permalink     TEXT,
            affiliate_url TEXT,               -- link de afiliado (do painel do ML)
            thumbnail     TEXT,
            coupon_code   TEXT,               -- cupom conhecido (opcional)
            coupon_note   TEXT,               -- regra do cupom, ex.: "min R$100"
            active        INTEGER DEFAULT 1,
            added_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS price_history (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id     TEXT NOT NULL,
            price          REAL NOT NULL,     -- preco atual de venda
            original_price REAL,              -- preco "de" que a loja anuncia (se houver)
            recorded_at    TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE INDEX IF NOT EXISTS idx_hist_prod_time
            ON price_history (product_id, recorded_at);
        """
    )
    _migrar(con)
    con.commit()
    con.close()


def _now():
    return datetime.now(timezone.utc).isoformat()


def add_product(product, db_path=None):
    """product: dict com id, title, permalink, affiliate_url, thumbnail, coupon_code, coupon_note."""
    con = _conn(db_path)
    con.execute(
        """
        INSERT INTO products (id, title, permalink, affiliate_url, thumbnail,
                              coupon_code, coupon_note, categoria, loja, active, added_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            permalink=excluded.permalink,
            affiliate_url=COALESCE(excluded.affiliate_url, products.affiliate_url),
            thumbnail=excluded.thumbnail,
            coupon_code=COALESCE(excluded.coupon_code, products.coupon_code),
            coupon_note=COALESCE(excluded.coupon_note, products.coupon_note),
            categoria=COALESCE(excluded.categoria, products.categoria),
            loja=COALESCE(excluded.loja, products.loja)
        """,
        (
            product["id"],
            product.get("title"),
            product.get("permalink"),
            product.get("affiliate_url"),
            product.get("thumbnail"),
            product.get("coupon_code"),
            product.get("coupon_note"),
            product.get("categoria"),
            product.get("loja") or "mercadolivre",
            _now(),
        ),
    )
    con.commit()
    con.close()


def get_products(only_active=True, db_path=None):
    con = _conn(db_path)
    q = "SELECT * FROM products"
    if only_active:
        q += " WHERE active = 1"
    rows = con.execute(q).fetchall()
    con.close()
    return [dict(r) for r in rows]


def record_price(product_id, price, original_price=None, db_path=None, recorded_at=None):
    con = _conn(db_path)
    con.execute(
        "INSERT INTO price_history (product_id, price, original_price, recorded_at) "
        "VALUES (?, ?, ?, ?)",
        (product_id, float(price), original_price, recorded_at or _now()),
    )
    con.commit()
    con.close()


def get_price_history(product_id, db_path=None):
    con = _conn(db_path)
    rows = con.execute(
        "SELECT price, original_price, recorded_at FROM price_history "
        "WHERE product_id = ? ORDER BY recorded_at ASC",
        (product_id,),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def latest_price(product_id, db_path=None):
    hist = get_price_history(product_id, db_path)
    return hist[-1] if hist else None


# ================= FILA / FREQUENCIA =================
def _migrar(con):
    cols = [r["name"] for r in con.execute("PRAGMA table_info(products)").fetchall()]
    if "cooldown_min" not in cols:
        con.execute("ALTER TABLE products ADD COLUMN cooldown_min INTEGER")
    if "last_posted_at" not in cols:
        con.execute("ALTER TABLE products ADD COLUMN last_posted_at TEXT")
    if "categoria" not in cols:
        con.execute("ALTER TABLE products ADD COLUMN categoria TEXT")
    if "loja" not in cols:
        con.execute("ALTER TABLE products ADD COLUMN loja TEXT DEFAULT 'mercadolivre'")
        con.execute("UPDATE products SET loja='mercadolivre' WHERE loja IS NULL")
    for extra, tipo in [("parcelas", "TEXT"), ("frete", "INTEGER"), ("pagamento", "TEXT"),
                        ("termo", "TEXT"), ("trend_score", "REAL"), ("mais_vendido", "INTEGER")]:
        if extra not in cols:
            con.execute(f"ALTER TABLE products ADD COLUMN {extra} {tipo}")
    if "urgente_desde" not in cols:
        con.execute("ALTER TABLE products ADD COLUMN urgente_desde TEXT")
    if "urgente_queda" not in cols:
        con.execute("ALTER TABLE products ADD COLUMN urgente_queda REAL")
    con.execute("CREATE TABLE IF NOT EXISTS estado (chave TEXT PRIMARY KEY, valor TEXT)")
    con.execute("""CREATE TABLE IF NOT EXISTS coupons (
        code     TEXT PRIMARY KEY,
        tipo     TEXT NOT NULL,        -- 'perc' ou 'fixo'
        valor    REAL NOT NULL,        -- 10 (=10%) ou 50 (=R$50)
        minimo   REAL DEFAULT 0,       -- valor minimo da compra
        teto     REAL,                 -- desconto maximo em R$ (opcional)
        validade TEXT,                 -- 'AAAA-MM-DD' (opcional)
        escopo   TEXT DEFAULT 'GLOBAL',-- 'GLOBAL' ou um ID de produto
        obs      TEXT,
        ativo    INTEGER DEFAULT 1)""")
    con.execute("""CREATE TABLE IF NOT EXISTS posts_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT, tier TEXT, price REAL, posted_at TEXT)""")


def set_cooldown(product_id, minutos, db_path=None):
    """Define a frequencia deste produto (em minutos). None = volta ao padrao do nivel."""
    con = _conn(db_path)
    con.execute("UPDATE products SET cooldown_min=? WHERE id=?", (minutos, product_id))
    con.commit(); con.close()


def marcar_postado(product_id, tier, price, db_path=None):
    con = _conn(db_path)
    agora = _now()
    con.execute("UPDATE products SET last_posted_at=? WHERE id=?", (agora, product_id))
    con.execute("INSERT INTO posts_log (product_id, tier, price, posted_at) VALUES (?,?,?,?)",
                (product_id, tier, price, agora))
    con.commit(); con.close()


def contar_posts(product_id=None, db_path=None):
    con = _conn(db_path)
    if product_id:
        n = con.execute("SELECT COUNT(*) c FROM posts_log WHERE product_id=?", (product_id,)).fetchone()["c"]
    else:
        n = con.execute("SELECT COUNT(*) c FROM posts_log").fetchone()["c"]
    con.close(); return n


# ================= CUPONS =================
def add_coupon(c, db_path=None):
    con = _conn(db_path)
    con.execute("""INSERT INTO coupons (code,tipo,valor,minimo,teto,validade,escopo,obs,ativo)
                   VALUES (?,?,?,?,?,?,?,?,1)
                   ON CONFLICT(code) DO UPDATE SET
                     tipo=excluded.tipo, valor=excluded.valor, minimo=excluded.minimo,
                     teto=excluded.teto, validade=excluded.validade, escopo=excluded.escopo,
                     obs=excluded.obs, ativo=1""",
                (c["code"].upper(), c["tipo"], float(c["valor"]), float(c.get("minimo") or 0),
                 c.get("teto"), c.get("validade"), (c.get("escopo") or "GLOBAL"), c.get("obs")))
    con.commit(); con.close()


def get_coupons(db_path=None, so_ativos=True):
    con = _conn(db_path)
    q = "SELECT * FROM coupons"
    if so_ativos:
        q += " WHERE ativo = 1"
    rows = con.execute(q).fetchall(); con.close()
    return [dict(r) for r in rows]


def del_coupon(code, db_path=None):
    con = _conn(db_path)
    con.execute("DELETE FROM coupons WHERE code=?", (code.upper(),))
    con.commit(); con.close()


# ================= ESTADO (chave/valor) =================
def estado_get(chave, default=None, db_path=None):
    con = _conn(db_path)
    r = con.execute("SELECT valor FROM estado WHERE chave=?", (chave,)).fetchone()
    con.close()
    return r["valor"] if r else default


def estado_set(chave, valor, db_path=None):
    con = _conn(db_path)
    con.execute("INSERT INTO estado (chave,valor) VALUES (?,?) "
                "ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor", (chave, str(valor)))
    con.commit(); con.close()


def marcar_urgente(product_id, queda_pct, db_path=None):
    con = _conn(db_path)
    con.execute("UPDATE products SET urgente_desde=?, urgente_queda=? WHERE id=?",
                (_now(), float(queda_pct), product_id))
    con.commit(); con.close()


def limpar_urgente(product_id, db_path=None):
    con = _conn(db_path)
    con.execute("UPDATE products SET urgente_desde=NULL, urgente_queda=NULL WHERE id=?", (product_id,))
    con.commit(); con.close()


def atualizar_dados(product_id, dados, db_path=None):
    """Atualiza campos vindos da lista (titulo, foto, parcelas, frete...)."""
    campos = {k: v for k, v in dados.items()
              if k in ("title", "thumbnail", "permalink", "parcelas", "frete",
                       "pagamento", "categoria") and v is not None}
    if not campos:
        return
    con = _conn(db_path)
    sets = ", ".join(f"{k}=?" for k in campos)
    con.execute(f"UPDATE products SET {sets} WHERE id=?",
                (*campos.values(), product_id))
    con.commit(); con.close()


def set_trend(product_id, score, db_path=None):
    con = _conn(db_path)
    con.execute("UPDATE products SET trend_score=? WHERE id=?", (float(score), product_id))
    con.commit(); con.close()


def set_termo(product_id, termo, db_path=None):
    con = _conn(db_path)
    con.execute("UPDATE products SET termo=? WHERE id=?", (termo, product_id))
    con.commit(); con.close()
