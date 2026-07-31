# Publicar o Garimpo Gamer Cupons no Cloudflare Pages — Fase 1

Objetivo desta fase: colocar o site no ar em **ggcupons.com.br**, com o
**ggcupons.com** redirecionando para ele. Publicacao manual (uma vez), so para
voce ver tudo funcionando. A automacao (site se atualizar sozinho) fica para a Fase 2.

Tempo estimado: ~30-40 min, sendo que a maior parte e esperar a propagacao de DNS.

---

## Passo 0 — Colocar os dois dominios no Cloudflare

Voce comprou os dominios na GoDaddy. Para usar dominio proprio no Pages e o
redirect, os dominios precisam usar o **DNS do Cloudflare** (plano gratuito).

1. Entre em https://dash.cloudflare.com e crie a conta (se ainda nao tem).
2. Clique em **Add a site** e digite `ggcupons.com.br`. Escolha o plano **Free**.
3. O Cloudflare mostra **dois nameservers** (algo como `xxx.ns.cloudflare.com`).
   Anote os dois.
4. Entre na **GoDaddy** -> seu dominio `ggcupons.com.br` -> **DNS / Nameservers**
   -> troque para "Nameservers personalizados" e cole os dois do Cloudflare. Salve.
5. Repita os passos 2-4 para `ggcupons.com` (ele tera **outros dois** nameservers).

> A propagacao leva de alguns minutos ate algumas horas. O Cloudflare te avisa
> por e-mail quando cada dominio ficar "Active". Voce pode seguir para o Passo 1
> enquanto espera.

---

## Passo 1 — Gerar o site REAL (com seus produtos)

No seu PC, dentro da pasta do projeto, rode em sequencia:

```
python sincronizar_lista.py --aplicar
python gerar_site.py
```

O primeiro puxa os produtos e precos reais da sua lista de afiliado; o segundo
gera a pasta `site/`. **E essa pasta `site/` que vai para o ar** — nao a versao
de amostra.

Confira: abra `site/index.html` no navegador e veja se os produtos reais aparecem.

---

## Passo 2 — Criar o projeto no Pages e subir a pasta

1. No painel do Cloudflare, menu lateral: **Workers & Pages** -> **Create** ->
   aba **Pages** -> **Upload assets**.
2. Nome do projeto: `ggcupons` (esse nome vira o endereco de teste
   `ggcupons.pages.dev`).
3. **Arraste a pasta `site` inteira** para a area de upload (ou clique em
   "select from computer" e selecione a pasta `site`).
4. Clique em **Deploy site**. Em alguns segundos ele publica.
5. Abra o link `https://ggcupons.pages.dev` que aparece — o site ja esta no ar
   nesse endereco temporario. Valide visual, grafico, filtros e links de produto.

> Guarde este projeto. Nas proximas publicacoes voce repete so os passos 1 e 2
> (nao precisa refazer dominio nem redirect).

---

## Passo 3 — Ligar o dominio ggcupons.com.br

1. Dentro do projeto `ggcupons` no Pages -> aba **Custom domains** ->
   **Set up a custom domain**.
2. Digite `ggcupons.com.br` -> **Continue** -> **Activate domain**.
   Como o dominio ja esta no Cloudflare, ele cria o registro DNS sozinho.
3. Adicione tambem `www.ggcupons.com.br` do mesmo jeito (opcional, mas
   recomendado — assim quem digitar "www" tambem chega).
4. Espere o status virar **Active** (poucos minutos). O certificado HTTPS e
   emitido automaticamente.

Pronto: o site responde em `https://ggcupons.com.br`.

---

## Passo 4 — Redirecionar ggcupons.com -> ggcupons.com.br

O `.com` deve **jogar** todo mundo para o `.com.br`. Isso se faz na zona do
`ggcupons.com` (que voce adicionou no Passo 0).

1. No painel, selecione o site **ggcupons.com**.
2. Antes da regra, o dominio precisa de um registro DNS para "existir" na borda:
   va em **DNS** -> **Add record** -> tipo **A**, nome `@`, IPv4 `192.0.2.1`
   (IP de exemplo, so para a regra ter onde agir), **Proxy: ativado (nuvem
   laranja)**. Salve. Faca o mesmo com nome `www`.
3. Va em **Rules** -> **Redirect Rules** -> **Create rule**.
   - Nome: `com para com.br`
   - **When incoming requests match**: escolha **All incoming requests**
     (ou Hostname contem `ggcupons.com`).
   - **Then... URL redirect** -> tipo **Dynamic**.
   - Expressao: `concat("https://ggcupons.com.br", http.request.uri.path)`
   - Status code: **301** (permanente). Marque **Preserve query string**.
4. Salve e **Deploy**.

Teste: abra `http://ggcupons.com` — deve cair em `https://ggcupons.com.br`.

---

## Passo 5 — Conferencia final

- [ ] `https://ggcupons.com.br` abre com HTTPS (cadeado) e mostra os produtos reais
- [ ] `www.ggcupons.com.br` tambem abre
- [ ] `ggcupons.com` redireciona para `ggcupons.com.br`
- [ ] Pagina de um produto: grafico interativo, filtros de periodo, semelhantes
- [ ] Links "Ver oferta" abrem o Mercado Livre com seu link de afiliado
- [ ] `https://ggcupons.com.br/sitemap.xml` e `/robots.txt` abrem

Quando isso tudo estiver ok, me chama que partimos para a **Fase 2**: o VPS que
sincroniza precos, regera o site e publica sozinho, sem seu PC ligado.

---

### Para as proximas publicacoes (enquanto nao temos a Fase 2)

So repita:
```
python sincronizar_lista.py --aplicar
python gerar_site.py
```
e no Pages: projeto `ggcupons` -> **Create deployment** -> arraste a pasta `site`.
Dominio e redirect continuam valendo — nao precisa refazer.
