"""Le a LISTA de afiliado do Mercado Livre (pagina /social/.../lists/...).

Esta pagina nao e bloqueada pelo ML e traz TODOS os produtos curados com preco,
preco 'de', parcelas e imagem — numa unica leitura. E a fonte principal do bot,
em vez de abrir a pagina de cada produto (que o ML bloqueia).
"""
import re

from bot import reader

# Extrator: le a estrutura de precos do ML (.andes-money-amount)
JS_LISTA = """
() => {
  const val = (el) => {
    if (!el) return null;
    const f = el.querySelector('.andes-money-amount__fraction');
    if (!f) return null;
    const c = el.querySelector('.andes-money-amount__cents');
    const frac = (f.textContent || '').replace(/\\D/g, '');
    const cents = c ? (c.textContent || '').replace(/\\D/g, '') : '';
    if (!frac) return null;
    return parseFloat(frac + '.' + (cents || '0').padEnd(2, '0').slice(0, 2));
  };

  const out = [];
  const vistos = new Set();

  document.querySelectorAll('a[href*="MLB"]').forEach(a => {
    const m = (a.href || '').match(/MLB-?\\d{6,}/);
    if (!m) return;
    const id = m[0].replace('-', '');
    if (vistos.has(id)) return;

    const card = a.closest('li, article, div.poly-card, div.andes-card') || a.parentElement;
    if (!card || !/R\\$/.test(card.innerText || '')) return;
    vistos.add(id);

    // titulo: a linha mais longa que nao seja selo/marca
    let titulo = (a.getAttribute('title') || '').trim();
    if (titulo.length < 10) {
      const h = card.querySelector('h2, h3, .poly-component__title, .poly-box');
      titulo = h ? (h.textContent || '').trim() : '';
    }
    if (titulo.length < 10) {
      const lixo = /^(mais vendido|oferta|patrocinado|frete|chegar|novo|usado|por\\s|\\d+%)/i;
      const linhas = (card.innerText || '').split('\\n')
        .map(s => s.trim())
        .filter(s => s.length > 14 && !lixo.test(s) && !/R\\$/.test(s));
      titulo = linhas[0] || '';
    }

    // precos: --previous e o "de"; o primeiro nao-previous e o preco atual
    const montantes = [...card.querySelectorAll('.andes-money-amount')];
    let de = null, por = null;
    for (const el of montantes) {
      const ehPrev = el.classList.contains('andes-money-amount--previous') ||
                     el.closest('s') !== null;
      const v = val(el);
      if (v === null) continue;
      if (ehPrev) { if (de === null) de = v; }
      else if (por === null) { por = v; }
    }

    // parcelas e frete
    const txt = card.innerText || '';
    const mp = txt.match(/(\\d{1,2})x\\s*(?:de\\s*)?R\\$\\s*([\\d\\.,]+)/i);
    const parcelas = mp ? (mp[1] + 'x R$ ' + mp[2]) : null;
    const frete = /frete gr[aá]tis|chegar[aá] gr[aá]tis|gr[aá]tis amanh/i.test(txt);
    const mo = txt.match(/(\\d{1,2})%\\s*OFF/i);
    const off = mo ? parseInt(mo[1]) : null;
    const pix = /no\\s*Pix/i.test(txt);
    const mais = /MAIS VENDIDO|OFERTA DO DIA/i.test(txt);

    // imagem (pode estar em lazy-load)
    const img = card.querySelector('img');
    const src = img ? (img.getAttribute('src') || img.getAttribute('data-src') ||
                       img.getAttribute('data-lazy') || '') : '';

    out.push({id, href: a.href.split('#')[0], titulo, de, por,
              parcelas, frete, off, pix, mais, img: src});
  });
  return out;
}
"""


def _rolar(page, vezes=6):
    """Rola a pagina para carregar os cards preguicosos (lazy-load)."""
    for _ in range(vezes):
        page.mouse.wheel(0, 1600)
        page.wait_for_timeout(1100)
    page.wait_for_timeout(1000)


def _proxima_pagina(page):
    """Tenta ir para a proxima pagina da lista. Devolve True se navegou."""
    seletores = [
        "li.andes-pagination__button--next:not(.andes-pagination__button--disabled) a",
        ".andes-pagination__button--next:not(.andes-pagination__button--disabled) a",
        "a[title='Seguinte']", "a[aria-label='Seguinte']",
        "a[title='Próxima']", "a[aria-label='Próxima']",
        "a[title='Proxima']", "a[rel='next']",
    ]
    for sel in seletores:
        try:
            el = page.query_selector(sel)
        except Exception:
            el = None
        if not el:
            continue
        try:
            el.scroll_into_view_if_needed(timeout=3000)
            el.click(timeout=5000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(3500)
            return True
        except Exception:
            continue
    return False


def ler(url_lista, headless=True, verbose=True, max_paginas=12):
    """Abre a lista e devolve os produtos com preco, percorrendo TODAS as paginas."""
    brutos = {}
    with reader.browser(headless=headless) as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(url_lista, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        reader._aceitar_cookies(page)

        for npag in range(1, max_paginas + 1):
            _rolar(page)

            if reader.bloqueado(page):
                if verbose:
                    print("[lista] BLOQUEADO pelo ML")
                break

            itens = page.evaluate(JS_LISTA)
            novos = 0
            for i in itens:
                if i.get("id") and i["id"] not in brutos:
                    brutos[i["id"]] = i
                    novos += 1
            if verbose:
                print(f"[lista] pagina {npag}: {len(itens)} lidos ({novos} novos)")

            # nada novo numa pagina seguinte -> para (evita loop)
            if npag > 1 and novos == 0:
                break
            # tenta avancar
            reader._aceitar_cookies(page)
            if not _proxima_pagina(page):
                break

    itens = list(brutos.values())
    limpos = []
    for i in itens:
        if i.get("por") is None:
            continue
        # se so veio um preco e ele esta em 'de', trata como preco atual
        if i.get("de") is not None and i["por"] is None:
            i["por"], i["de"] = i["de"], None
        # desconto: usa o % do card ou calcula
        desc = i.get("off")
        if not desc and i.get("de") and i["de"] > i["por"]:
            desc = round((i["de"] - i["por"]) / i["de"] * 100)
        i["desconto"] = desc or 0
        i["titulo"] = re.sub(r"\s+", " ", (i.get("titulo") or "")).strip()
        limpos.append(i)

    if verbose:
        print(f"[lista] {len(limpos)} produto(s) lidos no total ({len(brutos)} brutos)")
    return limpos
