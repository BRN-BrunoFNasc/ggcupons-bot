# Garimpo Gamer Cupons — Manual do Sistema

Bot de canal de ofertas: descobre produtos, monitora preço, monta o histórico,
gera o card visual e publica no Telegram 24h por dia.

*Atualizado em julho/2026.*

---

## 1. O que o sistema faz

1. **Cadastra produtos** — pela sua lista de afiliado do ML, por link avulso ou por descoberta automática.
2. **Monitora o preço** — varre os preços a cada 10 minutos e grava o histórico próprio.
3. **Classifica** — cada produto ganha uma **categoria** (Jogos, Consoles, Controles…) e um **nível** (menor preço, cupom, desconto forte…).
4. **Decide o que postar** — fila com rodízio entre categorias; queda de preço fura a fila.
5. **Monta o post** — card visual (foto, preço, % OFF, QR) + texto com De/Por, PIX, parcelas, cupom e link de afiliado.
6. **Publica no Telegram** — 24h, sem repetir o mesmo produto nem a mesma categoria em sequência.
7. **Painel de controle** — tela local para ver tudo e agir por botão (seção 4.1).

---

## 2. Instalação

```
pip install -r requirements.txt
playwright install chromium
```

Requer **Python 3.10+**. O Playwright é obrigatório: o Mercado Livre bloqueia
tanto a API quanto leitura simples de HTML, então tudo é lido por um navegador real.

---

## 2.1 Como o bot obtém os dados (arquitetura atual)

O Mercado Livre bloqueia páginas de produto e de busca para acesso automatizado,
mas **não bloqueia a página pública da sua lista de afiliado**. Ela virou a fonte
de dados do sistema:

```
Você adiciona produtos à lista no painel do ML
            ↓
sincronizar_lista.py  → lê a lista (1 página) e grava tudo no banco
            ↓                preço, preço "de", parcelas, frete, foto
vigia (a cada ciclo)  → relê a mesma página e detecta quedas
            ↓
publicação            → monta card e texto SÓ com dados do banco
                        (não acessa o Mercado Livre)
```

**Por que isso importa:** publicar não toca no ML, então não há risco de bloqueio
na hora de postar. E o monitoramento inteiro custa **uma leitura de página por
ciclo**, em vez de uma por produto.

Defina no `.env`:
```
ML_LISTA_URL=https://meli.la/SEU_LINK_DA_LISTA
MODO_LEVE=sim
```

## 3. Configuração (.env)

```
# ---- Mercado Livre ----
ML_CLIENT_ID=...              # do ML Developers (hoje pouco usado)
ML_CLIENT_SECRET=...
ML_MATT_WORD=...              # seu identificador de afiliado
ML_MATT_TOOL=...
ML_LINK_ESTRATEGIA=matt       # matt | lista | cru  (ver secao 8)
ML_LISTA_URL=https://meli.la/...   # sua lista de afiliado

# ---- Telegram ----
TELEGRAM_BOT_TOKEN=...        # do @BotFather
TELEGRAM_CHANNEL_ID=-100...   # ID do canal (o bot precisa ser admin)

# ---- Visual ----
LOGO_PATH=logo.png
TEMPLATE_PATH=template.png    # se existir, é usado como fundo do card
BRAND_NAME=GARIMPO GAMER CUPONS
CHANNEL_INVITE=https://t.me/+...

# ---- Fila de postagem ----
CICLO_MIN=10                  # de quanto em quanto tempo tenta postar
PAUSA_MADRUGADA=nao           # "sim" pausa 0h-6h
DESCONTO_FORTE_PCT=15
CD_MENOR_PRECO=240            # descanso por nível, em minutos
CD_CUPOM=480
CD_DESC_FORTE=720
CD_DESC_LEVE=1440
CD_SEM_DESCONTO=2880

# ---- Vigia de preços ----
VIGIA_INTERVALO_MIN=10        # varredura de preços
QUEDA_URGENTE_PCT=5           # queda que fura a fila
URGENTE_JANELA_MIN=90         # por quanto tempo segue urgente
URGENTE_GAP_MIN=20            # intervalo mínimo entre posts do mesmo produto

# ---- Descoberta ----
DESC_TERMOS=jogos-ps5|controle-ps5|...    # separados por |
DESC_MIN_DESCONTO=15
DESC_MAX_PRODUTOS=40
DESC_PRECO_MIN=50
DESC_PRECO_MAX=15000

# ---- Outras lojas (ainda inativas) ----
AMZ_TAG=                      # tag da Amazon (ex.: garimpo-20)
ALI_APP_KEY=                  # AliExpress Open Platform
ALI_APP_SECRET=
ALI_TRACKING_ID=
```

---

## 4. Comandos

### 4.1 Painel de controle (recomendado)

```
python painel.py            # porta padrão 8080
python painel.py 8090       # outra porta
python painel.py --flask    # força o servidor do Flask (fallback)
```
Abre em **http://127.0.0.1:8080** (use o IP, não `localhost`).
Usa o **waitress** como servidor — o servidor de desenvolvimento do Flask trava
no Windows resolvendo o nome da máquina. Se o painel ficar "carregando" para
sempre, é sinal de que caiu no Flask: instale o waitress (`pip install waitress`).
Para diagnosticar, abra `/ping` — deve responder "pong" na hora. É a forma mais prática de operar o sistema —
tudo que está nos comandos abaixo também está lá, por botão.

O painel mostra:

- **Resumo**: produtos ativos, quantos estão liberados, quantos em queda de preço,
  total de posts e **quantos estão sem link confiável**
- **Ações**: postar 1 ciclo, varrer preços, sincronizar sua lista, descobrir ofertas —
  com log ao vivo da execução
- **Ordem do rodízio** atual entre as categorias
- **Catálogo**: nível, preço, desconto, último post, tipo do link (oficial / montado /
  cru) e link clicável. Dá para **trocar a categoria**, **mudar a frequência**,
  **postar na hora**, **pausar** e **apagar** direto na tabela
- **Cupons**: formulário para cadastrar (tipo, valor, mínimo, teto, validade, escopo)
  e lista mostrando quais estão vencidos
- **Posts recentes**: o que foi publicado, quando, em que nível e por qual preço

Atualiza sozinho a cada 30s. É local (`127.0.0.1`) — **não exponha na internet**,
não tem senha.

### Cadastro de produtos

| Comando | O que faz |
|---|---|
| `python sincronizar_lista.py "URL" --aplicar` | Lê sua lista de afiliado do ML e cadastra tudo |
| `python sincronizar.py --aplicar` | Cadastra a partir do arquivo `meus_links.txt` |
| `python add_produto.py "URL" --link "AFILIADO"` | Cadastra um produto avulso |
| `python descobrir.py` | Procura ofertas no ML e **só mostra** |
| `python descobrir.py --cadastrar` | Procura e cadastra automaticamente |

### Operação

| Comando | O que faz |
|---|---|
| `python run_loop.py --publicar` | **Modo 24h**: vigia preços e posta em rodízio |
| `python run_ciclo.py` | Um ciclo só (prévia) |
| `python run_ciclo.py --publicar` | Um ciclo só (posta) |
| `python post_produto.py MLB123 --publicar` | Força o post de um produto |
| `python run_record.py` | Grava os preços do dia lendo a sua lista (1 página, via vigia) |

### Gestão

| Comando | O que faz |
|---|---|
| `python listar.py` | Catálogo: loja, categoria, nível, frequência, preço |
| `python links.py` | Mostra que tipo de link cada produto está usando |
| `python frequencia.py MLB123 15` | Frequência própria (minutos) — `auto` volta ao padrão |
| `python remover.py MLB123` | Pausa um produto (`--apagar` remove de vez) |
| `python remover.py --duplicados` | Encontra produtos repetidos |
| `python remover.py --categoria MLB123 Jogos` | Corrige a categoria |
| `python limpar.py` | Mostra o que existe (não apaga) |
| `python limpar.py --tudo` | **Zera o catálogo** para recomeçar (`--manter-cupons` preserva cupons) |

### Cupons

| Comando | O que faz |
|---|---|
| `python cupons.py add CODIGO perc 10 --minimo 500 --teto 50 --validade 2026-08-31` | Cadastra cupom |
| `python cupons.py add CODIGO fixo 30 --escopo MLB123` | Cupom de um produto só |
| `python cupons.py list` | Lista os cupons e se estão vencidos |
| `python cupons.py rm CODIGO` | Remove |

### Testes

```
python tests/test_pipeline.py    # histórico -> texto -> card
python tests/test_fila.py        # níveis e descanso
python tests/test_cupons.py      # teto, mínimo, validade, escopo
python tests/test_rodizio.py     # rodízio de categorias e furo de fila
```

---

## 5. Como o sistema decide o que postar

### Níveis (definem prioridade e descanso)

| Nível | Quando | Descanso padrão |
|---|---|---|
| 🔥 MENOR_PRECO | bate o mínimo de 30/60/90 dias | 4h |
| 🎟️ CUPOM | existe cupom válido aplicável | 8h |
| 💥 DESCONTO_FORTE | De/Por ≥ 15% | 12h |
| 🏷️ DESCONTO_LEVE | qualquer De/Por | 24h |
| ⚪ SEM_DESCONTO | preço cheio | 48h |

### Rodízio de categorias

O bot **não** posta sempre o de maior desconto — isso faria o canal virar só monitores.
Ele percorre uma sequência montada a partir dos `slots` de cada categoria:

`Jogos → Consoles → Gift Card → Controles → Acessórios → Fones → Monitores → Outros → Jogos → Consoles → Controles → Acessórios → Jogos` (e recomeça)

Dentro da categoria da vez, vence o produto de maior nível. Nunca há duas
postagens seguidas da mesma categoria.

### Furo de fila (queda de preço)

A cada 10 minutos o vigia varre os preços. Se um produto cai **5% ou mais**, ele
é marcado como urgente e **fura a fila** no ciclo seguinte, com o selo
"⚡ BAIXOU AGORA". Proteções: não repete o mesmo produto antes de 20 min, e a
urgência expira em 90 min.

### Ordem de decisão

```
1. tem produto com queda recente?      -> posta esse
2. senão, próxima categoria do rodízio -> melhor produto liberado dela
3. senão, qualquer produto liberado
4. senão, não posta neste ciclo
```

---

## 6. Arquivo `categorias.json`

Controla prioridade, cota, descanso e classificação. **Edite à vontade** — não precisa mexer em código.

```json
{
  "nome": "Jogos",
  "prioridade": 100,      // ordena dentro do mesmo nível
  "cota": 14,             // máx. por rodada de descoberta
  "cooldown_min": 360,    // descanso da categoria (sobrepõe o do nível)
  "slots": 3,             // quantas vezes aparece em um ciclo de rodízio
  "palavras": [...],      // o que identifica a categoria
  "bloqueio": [...]       // o que exclui da categoria
}
```

**Como a classificação funciona:** vence a palavra-chave **mais específica** (a
mais longa encontrada no título); acentos são ignorados; se o título tiver
qualquer palavra de `bloqueio`, a categoria é descartada.

Precedência do descanso: **frequência manual do produto** > **cooldown da categoria** > **padrão do nível**.

---

## 7. Cupons

Não é possível "testar" cupom no checkout do ML. O sistema trabalha com a
**regra** do cupom, que você cadastra uma vez:

- calcula e exibe o **preço final com cupom**
- só aplica se o produto atingir o **mínimo**
- respeita o **teto** de desconto
- **esconde sozinho quando vence** — é isso que garante que só divulga cupom válido
- escolhe o **melhor cupom** quando mais de um se aplica
- cupom `GLOBAL` vale para tudo; com `--escopo MLB123` vale só num produto

---

## 8. Link de afiliado (ponto em aberto)

O ML **não permite montar link de afiliado por conta própria** de forma
confirmada — o link oficial carrega um token `ref=` assinado. Três estratégias
disponíveis em `ML_LINK_ESTRATEGIA`:

| Valor | Como funciona | Situação |
|---|---|---|
| `matt` | URL do produto + `matt_word`/`matt_tool` | **em teste** — verificar em janela anônima (auto-clique não conta) |
| `lista` | posta o link da sua lista (`meli.la/...`) | atribuição garantida, mas cai na lista, não no produto |
| `cru` | sem afiliado | só para testes |

Fluxo recomendado enquanto isso não fecha: adicione produtos à sua lista no
painel e rode `sincronizar_lista.py`.

---

## 8.1 Visual do card

O card é montado em três modos, nesta ordem de prioridade:

| Modo | Quando é usado | Arquivo |
|---|---|---|
| **Template com zonas** | existe `template.png` (arte de designer com áreas reservadas) | `TEMPLATE_PATH` |
| **Arte de fundo** | existe `fundo.png` (arte gerada por IA) | `FUNDO_PATH` |
| **Desenhado** | nenhum dos dois | — |

**Modo arte de fundo (recomendado sem designer):** a IA gera apenas a arte
atmosférica de fundo — sem layout, sem áreas reservadas, sem texto. O código
desenha por cima, com precisão: véu escuro no topo e na base, logo e marca,
painel branco com sombra para a foto, selo de % OFF, faixa de preço, QR e
chamada. Como a estrutura é toda desenhada, não importa se a IA "errou" o
layout — só a atmosfera dela é aproveitada.

Para usar: gere a arte, salve como `fundo.png` na pasta do projeto e pronto.

## 9. Outras lojas

O sistema é multi-loja: cada loja é um adaptador em `bot/lojas/` que implementa
a mesma interface. Toda a lógica (histórico, níveis, rodízio, cupons, card,
Telegram) funciona igual para qualquer uma.

| Loja | Situação | Observação |
|---|---|---|
| **Mercado Livre** | ✅ ativo | Navegador (API e HTML bloqueados) |
| **AliExpress** | ⏳ aguardando chaves | Tem API oficial completa: ofertas, preços, cupons e **geração de link**. Aprovação em 1-2 dias |
| **Amazon** | ⏳ aguardando tag | Link de afiliado é trivial (`?tag=seu-20`). A PA-API foi descontinuada em mai/2026 (Creators API exige vendas recentes), então a leitura será por navegador |

---

## 10. Estrutura de arquivos

```
ofertas-bot/
├── bot/
│   ├── config.py         lê o .env
│   ├── reader.py         leitura de produto via navegador (Playwright + anti-detecção)
│   ├── descoberta.py     busca ofertas no ML e filtra
│   ├── vigia.py          varredura de preços e detecção de quedas
│   ├── database.py       SQLite (produtos, histórico, cupons, posts, estado)
│   ├── analytics.py      mínimas de 30/60/90 dias
│   ├── categorias.py     classificação por palavra-chave
│   ├── cupons.py         regras e cálculo do preço com cupom
│   ├── fila.py           níveis, rodízio e urgência
│   ├── ciclo.py          um ciclo de postagem
│   ├── message.py        texto do post (HTML)
│   ├── imagem.py         card visual (com ou sem template)
│   ├── telegram_bot.py   envio ao canal
│   ├── link_ml.py        estratégias de link de afiliado
│   └── lojas/            adaptadores: mercadolivre, amazon, aliexpress
├── painel.py             painel de controle local (Flask)
├── templates/painel.html interface do painel
├── categorias.json       suas regras de categoria
├── sincronizar_lista.py  lê sua lista de afiliado do ML (pública, sem login)
├── pegar_id_canal.py     descobre o ID de um canal novo do Telegram
├── teste_servidor.py     diagnóstico de rede/porta (sem Flask)
├── meus_links.txt        produtos colados à mão (alternativa à lista)
├── limpar.py             zera o catálogo
├── data/                 banco, cards gerados
└── tests/                testes automáticos
```

---

## 11. Rodar 24h numa VPS

```
# na VPS (Ubuntu)
sudo apt update && sudo apt install -y python3-pip
pip install -r requirements.txt
playwright install --with-deps chromium

# manter rodando como serviço (systemd)
sudo nano /etc/systemd/system/ofertas.service
```

```ini
[Unit]
Description=Bot Garimpo Gamer
After=network.target

[Service]
WorkingDirectory=/caminho/ofertas-bot
ExecStart=/usr/bin/python3 run_loop.py --publicar
Restart=always
RestartSec=30
User=SEU_USUARIO

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl enable --now ofertas
sudo systemctl status ofertas       # ver situação
journalctl -u ofertas -f            # ver os logs ao vivo
```

---

## 12.1 Bloqueio do Mercado Livre (importante)

O ML barra acesso automatizado em camadas. Já enfrentamos três:

| Camada | Sintoma | Situação |
|---|---|---|
| API oficial | `PolicyAgent / PA_UNAUTHORIZED` | bloqueada, sem volta |
| Leitura de HTML | redireciona para verificação | bloqueada |
| Navegador automatizado | `/gz/account-verification` | contornável com cuidado |

**O que provoca:** volume. A descoberta automática varre ~2.000 páginas/dia —
foi o que disparou o bloqueio. Curando os produtos na mão e lendo só o catálogo,
o volume cai para ~200/dia.

**Defesas implementadas:**

- **Perfil persistente** (`data/perfil_navegador/`): cookies e histórico
  sobrevivem entre execuções, dando cara de visitante recorrente
- **`python aquecer.py`**: navega o ML como humano para criar reputação no
  perfil. Rode uma vez, e de novo se voltar a bloquear
- **MODO_LEVE=sim** (padrão): desliga a descoberta e lê só o catálogo
- **Ritmo humano**: pausa sorteada entre 8 e 22s entre páginas
- **Teto diário**: `LIMITE_DIARIO_PAGINAS` (400 por padrão)
- **Recuo automático**: ao detectar bloqueio, o vigia para em vez de insistir

**Se bloquear mesmo assim:** espere algumas horas, rode `aquecer.py`, e aumente
`VIGIA_INTERVALO_MIN` para 30 ou 60.

## 12. Problemas conhecidos

- **Painel carrega para sempre / porta bloqueada (`WinError 10013`)**: o Windows
  (Hyper-V/WSL) reserva faixas de portas — a 8080 costuma cair numa delas. O painel
  já detecta e troca de porta sozinho, avisando qual usou. Para ver as faixas
  reservadas: `netsh interface ipv4 show excludedportrange protocol=tcp`.
  Para testar o ambiente sem Flask: `python teste_servidor.py 8090`.
- **Painel carregando mesmo com a porta livre**: o servidor de desenvolvimento do
  Flask trava no Windows. Instale o waitress (`pip install waitress`) — o painel
  usa ele automaticamente. Teste com `/ping`.
- **`disk I/O error` no banco**: o SQLite não aceita modo WAL em pasta
  sincronizada. O código já força o modo clássico; se aparecerem arquivos
  `ofertas.db-wal` ou `ofertas.db-shm`, apague-os com o bot parado.
- **Painel e `run_loop.py` juntos**: pode rodar os dois ao mesmo tempo; o banco
  espera até 15s pelo outro processo em vez de falhar.

- **ML pede verificação** ("account-verification"): o Playwright já usa
  anti-detecção. Se voltar a acontecer, aumente `VIGIA_INTERVALO_MIN` — varredura
  agressiva demais chama atenção.
- **Preço não lido**: layout novo do ML. Rode com `--ver` para ver a página.
- **Categoria errada**: ajuste `palavras`/`bloqueio` no `categorias.json`.
- **Post sem histórico**: normal nos primeiros dias; a frase "menor preço em X dias"
  só aparece com 3+ dias e 3+ registros.


## 13. Auditoria (jul/2026)

Revisão completa antes do deploy na Cloudflare:

- **Corrigido (grave):** páginas de produto e a de links eram geradas sem rodapé
  e sem fechar o HTML (resíduo da migração `RODAPE` → `_rodape()`).
- **Corrigido:** `run_record.py` agora usa o vigia (lê a lista de afiliado) em vez
  de abrir a página de cada produto, que o ML bloqueia.
- **Proteção:** `SITE_TEMA=escuro` está desatualizado e agora cai no `claro` com aviso.
- **Avisos adicionados** em `add_produto.py` e `sincronizar.py` (fluxos que dependem
  da página de produto) apontando para `sincronizar_lista.py`.
- **Automatizado:** `site/responsivo.html` é recriado a cada build.
- Validações que passam no build: HTML fechado + rodapé em todas as páginas,
  links internos íntegros, sitemap correto, 23 checagens de `testar_site.py`,
  4 suítes de testes unitários, 43 módulos importando.
