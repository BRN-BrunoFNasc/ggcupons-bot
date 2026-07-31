"""Grafico de historico de preco em SVG puro (sem JavaScript, rapido e indexavel)."""
from datetime import datetime, timezone


def _parse(ts):
    try:
        t = datetime.fromisoformat(ts)
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _fmt(v):
    return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def svg(historico, largura=760, altura=280, cor="#2ee6a0", cor_min="#ff5a3c"):
    """Recebe [{price, recorded_at}] e devolve um SVG do historico."""
    pontos = [(p := _parse(h["recorded_at"]), h["price"]) for h in historico]
    pontos = [(t, v) for t, v in pontos if t and v]
    if len(pontos) < 2:
        return ('<div class="sem-grafico">Histórico ainda sendo construído — '
                'volte em alguns dias.</div>')

    pontos.sort(key=lambda x: x[0])
    ts = [p[0].timestamp() for p in pontos]
    vs = [p[1] for p in pontos]
    t0, t1 = min(ts), max(ts)
    v0, v1 = min(vs), max(vs)
    if t1 == t0:
        t1 = t0 + 1
    folga = (v1 - v0) * 0.18 or (v1 * 0.05 or 1)
    vmin, vmax = v0 - folga, v1 + folga

    ml, mr, mt, mb = 74, 18, 20, 34
    lg, al = largura - ml - mr, altura - mt - mb

    def X(t):
        return ml + (t - t0) / (t1 - t0) * lg

    def Y(v):
        return mt + (vmax - v) / (vmax - vmin) * al

    linha = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in zip(ts, vs))
    area = f"{ml},{mt+al} " + linha + f" {ml+lg},{mt+al}"

    # grade e eixo Y
    grade = []
    for i in range(4):
        v = vmin + (vmax - vmin) * i / 3
        y = Y(v)
        grade.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml+lg}" y2="{y:.1f}" '
                     f'stroke="rgba(255,255,255,.08)" stroke-width="1"/>')
        grade.append(f'<text x="{ml-10}" y="{y+4:.1f}" text-anchor="end" '
                     f'font-size="11" fill="rgba(255,255,255,.45)">{_fmt(v)}</text>')

    # datas
    datas = []
    for i in (0, len(pontos) // 2, len(pontos) - 1):
        t, _ = pontos[i]
        datas.append(f'<text x="{X(t.timestamp()):.1f}" y="{altura-10}" '
                     f'text-anchor="middle" font-size="11" '
                     f'fill="rgba(255,255,255,.45)">{t.strftime("%d/%m")}</text>')

    # marcas: menor preco e preco atual
    i_min = vs.index(min(vs))
    marcas = (f'<circle cx="{X(ts[i_min]):.1f}" cy="{Y(vs[i_min]):.1f}" r="5" fill="{cor_min}"/>'
              f'<circle cx="{X(ts[-1]):.1f}" cy="{Y(vs[-1]):.1f}" r="5" fill="{cor}"/>')

    return f'''<svg viewBox="0 0 {largura} {altura}" class="gr" role="img"
  aria-label="Histórico de preço">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{cor}" stop-opacity=".28"/>
    <stop offset="100%" stop-color="{cor}" stop-opacity="0"/>
  </linearGradient></defs>
  {''.join(grade)}
  <polygon points="{area}" fill="url(#g)"/>
  <polyline points="{linha}" fill="none" stroke="{cor}" stroke-width="2.5"
    stroke-linejoin="round" stroke-linecap="round"/>
  {marcas}{''.join(datas)}
</svg>'''


def spark(historico, w=200, h=44, cor="#15803d"):
    """Mini-grafico de linha para caber num card."""
    pts = [(_parse(x["recorded_at"]), x["price"]) for x in historico]
    pts = [(t, v) for t, v in pts if t and v]
    if len(pts) < 2:
        return ""
    pts.sort(key=lambda x: x[0])
    vs = [v for _, v in pts]
    vmin, vmax = min(vs), max(vs)
    rng = (vmax - vmin) or 1
    n = len(vs)
    pl = " ".join(f"{i/(n-1)*w:.1f},{h-4-(v-vmin)/rng*(h-8):.1f}"
                  for i, v in enumerate(vs))
    fim_baixo = vs[-1] <= vs[0]
    c = cor if fim_baixo else "#9ca3af"
    return (f'<svg viewBox="0 0 {w} {h}" class="spark" preserveAspectRatio="none">'
            f'<polyline points="{pl}" fill="none" stroke="{c}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/></svg>')
