#!/usr/bin/env python3
"""Teste minimo de servidor - sem Flask, sem banco, so Python puro.

    python teste_servidor.py

Serve para descobrir se o problema e o nosso codigo ou o ambiente
(firewall, antivirus, proxy do navegador).
"""
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORTA = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080

PAGINA = b"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Teste</title></head>
<body style="background:#0e1a14;color:#2ee6a0;font-family:sans-serif;text-align:center;padding:60px">
<h1>FUNCIONOU!</h1>
<p style="color:#eaf3ee">O servidor Python responde normalmente nesta maquina.</p>
<p style="color:#7d9a8c">Pode fechar esta aba e voltar ao terminal.</p>
</body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"  -> recebi requisicao: {self.path}", flush=True)
        corpo = b"pong" if self.path == "/ping" else PAGINA
        tipo = "text/plain" if self.path == "/ping" else "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *a):
        pass  # silencia o log padrao


if __name__ == "__main__":
    print("\n== TESTE DE SERVIDOR (Python puro) ==")
    print("  Python  :", sys.version.split()[0])
    print("  Hostname:", socket.gethostname())

    # a porta esta livre?
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", PORTA))
        s.close()
        print(f"  Porta {PORTA}: LIVRE")
    except OSError as e:
        print(f"  Porta {PORTA}: OCUPADA ({e})")
        print(f"  -> tente outra: python teste_servidor.py 8090")
        sys.exit(1)

    srv = HTTPServer(("127.0.0.1", PORTA), H)
    print(f"\n  SERVIDOR NO AR em http://127.0.0.1:{PORTA}")
    print(f"  Abra no navegador. Ctrl+C para parar.\n", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  encerrado.")
