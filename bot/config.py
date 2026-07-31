"""Carrega as configuracoes a partir do arquivo .env."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass  # dotenv e opcional; variaveis de ambiente do sistema tambem funcionam


def _get(name, default=""):
    """Le uma variavel do .env.

    Campo vazio seguido de comentario (ex.: 'LINK_BIO=   # explique aqui') e lido
    pelo dotenv como se o comentario fosse o valor. Aqui isso vira vazio.
    """
    v = os.environ.get(name, default)
    v = (v or "").strip()
    if v.startswith("#"):
        return default if not str(default).startswith("#") else ""
    # remove comentario no fim da linha ("valor   # nota"), preservando URLs com #
    if " #" in v and not v.startswith("http"):
        v = v.split(" #", 1)[0].strip()
    return v


ML_CLIENT_ID = _get("ML_CLIENT_ID")
ML_CLIENT_SECRET = _get("ML_CLIENT_SECRET")
ML_AFFILIATE_TAG = _get("ML_AFFILIATE_TAG")

TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = _get("TELEGRAM_CHANNEL_ID")

MIN_DISCOUNT_PERCENT = float(_get("MIN_DISCOUNT_PERCENT", "5") or 5)
HISTORY_WINDOWS = [
    int(x) for x in (_get("HISTORY_WINDOWS", "30,60,90") or "30,60,90").split(",") if x.strip()
]

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "ofertas.db"


# ===== Marca / canal (para o card visual) =====
BRAND_NAME = _get("BRAND_NAME", "GARIMPO GAMER CUPONS") or "GARIMPO GAMER CUPONS"
CHANNEL_INVITE = _get("CHANNEL_INVITE", "https://t.me/+LXsOkrepjKY0MTJh") or "https://t.me/+LXsOkrepjKY0MTJh"
LOGO_PATH = _get("LOGO_PATH", "")  # opcional: caminho de um PNG do seu logo

# ===== Template do card (imagem de fundo feita por IA) =====
TEMPLATE_PATH = _get("TEMPLATE_PATH", "template.png")
# Zonas do template (x0,y0,x1,y1) em imagem 1080x1080 - ajustaveis no .env
def _zone(name, default):
    v = _get(name, "")
    try:
        p = [int(x) for x in v.split(",")]
        return tuple(p) if len(p) == 4 else default
    except Exception:
        return default

ZONA_LOGO  = _zone("ZONA_LOGO",  (40, 18, 165, 143))
ZONA_FOTO  = _zone("ZONA_FOTO",  (130, 190, 950, 760))
ZONA_PRECO = _zone("ZONA_PRECO", (210, 790, 870, 880))
ZONA_QR    = _zone("ZONA_QR",    (915, 925, 1045, 1055))
ZONA_CTA   = _zone("ZONA_CTA",   (55, 935, 880, 1055))

# ===== Fila de postagem =====
CICLO_MIN = int(_get("CICLO_MIN", "10") or 10)          # de quantos em quantos min o bot acorda
DESCONTO_FORTE_PCT = float(_get("DESCONTO_FORTE_PCT", "15") or 15)
PAUSA_MADRUGADA = _get("PAUSA_MADRUGADA", "nao").lower() in ("sim", "true", "1")

# tempo de descanso padrao por nivel (minutos)
COOLDOWNS = {
    "MENOR_PRECO":    int(_get("CD_MENOR_PRECO", "240") or 240),     # 4h
    "CUPOM":          int(_get("CD_CUPOM", "480") or 480),           # 8h
    "DESCONTO_FORTE": int(_get("CD_DESC_FORTE", "720") or 720),      # 12h
    "DESCONTO_LEVE":  int(_get("CD_DESC_LEVE", "1440") or 1440),     # 24h
    "SEM_DESCONTO":   int(_get("CD_SEM_DESCONTO", "2880") or 2880),  # 48h
}
PRIORIDADES = {
    "MENOR_PRECO": 100, "CUPOM": 80, "DESCONTO_FORTE": 70,
    "DESCONTO_LEVE": 50, "SEM_DESCONTO": 20,
}

# ===== Parametros de afiliado do Mercado Livre =====
# Vistos na URL final do seu link de afiliado (matt_word / matt_tool)
ML_MATT_WORD = _get("ML_MATT_WORD", "")
ML_MATT_TOOL = _get("ML_MATT_TOOL", "")

# ===== Descoberta automatica de ofertas =====
_urls = _get("DESCOBERTA_URLS", "")
DESCOBERTA_URLS = [u.strip() for u in _urls.split("|") if u.strip()] or [
    "https://www.mercadolivre.com.br/ofertas",
    "https://www.mercadolivre.com.br/ofertas?category=MLB1144",  # Games
    "https://www.mercadolivre.com.br/ofertas?category=MLB1648",  # Informatica
    "https://www.mercadolivre.com.br/ofertas?category=MLB1000",  # Eletronicos
]
DESC_MIN_DESCONTO = int(_get("DESC_MIN_DESCONTO", "15") or 15)
DESC_MAX_PRODUTOS = int(_get("DESC_MAX_PRODUTOS", "40") or 40)
DESC_PRECO_MIN = float(_get("DESC_PRECO_MIN", "50") or 50)
DESC_PRECO_MAX = float(_get("DESC_PRECO_MAX", "15000") or 15000)
DESC_INTERVALO_H = int(_get("DESC_INTERVALO_H", "6") or 6)

# ===== Termos de busca do seu nicho (viram URLs de busca no ML) =====
_termos = _get("DESC_TERMOS", "")
DESC_TERMOS = [t.strip() for t in _termos.split("|") if t.strip()] or [
    "jogos-ps5", "jogos-ps4", "jogos-xbox-series-x", "jogos-xbox-one",
    "controle-ps5", "controle-xbox", "controle-nintendo-switch",
    "monitor-gamer", "monitor-portatil",
    "console-playstation-5", "console-xbox-series-s", "nintendo-switch",
    "gift-card-playstation", "gift-card-xbox", "gift-card-steam",
]
# Palavras que o titulo PRECISA conter (qualquer uma). Vazio = aceita tudo.
_ok = _get("DESC_PALAVRAS_OK", "")
DESC_PALAVRAS_OK = [w.strip().lower() for w in _ok.split("|") if w.strip()] or [
    "ps5", "ps4", "playstation", "xbox", "nintendo", "switch", "controle",
    "monitor", "console", "gift card", "gift-card", "headset", "jogo", "game",
]
# Palavras que descartam o produto
_no = _get("DESC_PALAVRAS_BLOQUEIO", "")
DESC_PALAVRAS_BLOQUEIO = [w.strip().lower() for w in _no.split("|") if w.strip()] or [
    "toalha", "colcha", "capa de sofa", "peruca", "suplemento", "racao",
    "adesivo", "skin ", "case ", "pelicula", "cabo usb", "carregador de celular",
]

# ===== Rodizio de categorias e vigia de precos =====
VIGIA_INTERVALO_MIN = int(_get("VIGIA_INTERVALO_MIN", "10") or 10)   # varredura de precos
QUEDA_URGENTE_PCT = float(_get("QUEDA_URGENTE_PCT", "5") or 5)       # queda que fura a fila
URGENTE_JANELA_MIN = int(_get("URGENTE_JANELA_MIN", "90") or 90)     # por quanto tempo fica urgente
URGENTE_GAP_MIN = int(_get("URGENTE_GAP_MIN", "20") or 20)           # gap minimo entre posts do mesmo item

# ===== Outras lojas =====
AMZ_TAG = _get("AMZ_TAG", "")              # sua tag de afiliado Amazon (ex.: garimpo-20)
_amz = _get("AMZ_URLS", "")
AMZ_URLS = [u.strip() for u in _amz.split("|") if u.strip()]
ALI_APP_KEY = _get("ALI_APP_KEY", "")      # AliExpress Open Platform
ALI_APP_SECRET = _get("ALI_APP_SECRET", "")
ALI_TRACKING_ID = _get("ALI_TRACKING_ID", "")

# URL publica da sua vitrine de afiliado do ML (/social/SEU_USUARIO)
ML_VITRINE = _get("ML_VITRINE", "https://www.mercadolivre.com.br/social/fernandesbruno20211130222643")

# Como montar o link de afiliado do ML:
#   "matt"  -> URL do produto + matt_word/matt_tool  (a confirmar no painel)
#   "lista" -> posta o link da sua LISTA (atribuicao garantida, cai na lista)
#   "cru"   -> sem afiliado (so para testes)
ML_LINK_ESTRATEGIA = _get("ML_LINK_ESTRATEGIA", "matt")
ML_LISTA_URL = _get("ML_LISTA_URL", "")   # ex.: https://meli.la/2byuhxD

# Arte de fundo gerada por IA (a estrutura e desenhada por cima pelo codigo)
FUNDO_PATH = _get("FUNDO_PATH", "fundo.png")

# ===== Cores do card (aceita #RRGGBB) =====
def _cor(nome, padrao):
    v = _get(nome, "") or padrao
    v = v.lstrip("#")
    try:
        return tuple(int(v[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return tuple(int(padrao[i:i+2], 16) for i in (0, 2, 4))

COR_BARRA   = _cor("COR_BARRA",   "123A2C")   # topo (faixa da marca)
COR_RODAPE  = _cor("COR_RODAPE",  "0E1A14")   # rodape
COR_PRECO   = _cor("COR_PRECO",   "FF5A3C")   # faixa do preco
COR_LINHA   = _cor("COR_LINHA",   "2EE6A0")   # linha de destaque
COR_TEXTO2  = _cor("COR_TEXTO2",  "2EE6A0")   # 2a linha do rodape

# ===== Ritmo de acesso (evita bloqueio do Mercado Livre) =====
# MODO_LEVE: desliga a descoberta automatica e usa ritmo humano.
# E o modo recomendado quando voce cura os produtos na mao.
MODO_LEVE = _get("MODO_LEVE", "sim").lower() in ("sim", "true", "1")
PAUSA_MIN_SEG = float(_get("PAUSA_MIN_SEG", "8") or 8)     # pausa minima entre paginas
PAUSA_MAX_SEG = float(_get("PAUSA_MAX_SEG", "22") or 22)   # pausa maxima (sorteada)
LIMITE_DIARIO_PAGINAS = int(_get("LIMITE_DIARIO_PAGINAS", "400") or 400)

# Pasta do perfil do navegador (deixe vazio para o padrao do sistema).
# Nao aponte para dentro da pasta do projeto se ela estiver em area protegida.
PERFIL_NAVEGADOR = _get("PERFIL_NAVEGADOR", "")

# Assinatura sob o nome da marca no card
BRAND_SUB = _get("BRAND_SUB", "OFERTAS DE GAMES E TECH")

# ===== Links do projeto (pagina de links / redes) =====
LINK_BIO   = _get("LINK_BIO", "")        # sua pagina com todos os links
INSTAGRAM  = _get("INSTAGRAM", "")
TIKTOK     = _get("TIKTOK", "")
YOUTUBE    = _get("YOUTUBE", "")
WHATSAPP   = _get("WHATSAPP", "")        # link do Canal do WhatsApp

# Endereco final do site (para sitemap, canonical e og:url)
SITE_URL = _get("SITE_URL", "https://ggcupons.com.br").rstrip("/")

# Tema do site: "escuro" (gamer) ou "claro" (comparador de precos)
SITE_TEMA = _get("SITE_TEMA", "escuro")
