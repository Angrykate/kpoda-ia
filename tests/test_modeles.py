import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from src.modeles import ErreurModele, modele_gemini


def serveur(statut, corps):
    vus = {}

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            vus["chemin"] = self.path
            vus["cle"] = self.headers.get("x-goog-api-key")
            vus["corps"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_response(statut)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(corps).encode())

        def log_message(self, *a):
            pass

    s = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, vus


def test_appel_gemini_nominal():
    s, vus = serveur(200, {"candidates": [{"content": {"parts": [{"text": "{\"a\": 1}"}]}}]})
    m = modele_gemini("gemini-test", cle="CLE", url_base=f"http://127.0.0.1:{s.server_port}")
    assert m("bonjour") == '{"a": 1}'
    assert vus["chemin"] == "/models/gemini-test:generateContent"
    assert vus["cle"] == "CLE"
    assert vus["corps"]["contents"][0]["parts"][0]["text"] == "bonjour"
    s.shutdown()


@pytest.mark.parametrize("code,mot", [(429, "limite"), (403, "clé"), (404, "introuvable")])
def test_erreurs_lisibles_sans_fuite_de_cle(code, mot):
    s, _ = serveur(code, {"error": "x"})
    m = modele_gemini("gemini-test", cle="SECRET", url_base=f"http://127.0.0.1:{s.server_port}")
    with pytest.raises(ErreurModele) as e:
        m("bonjour")
    assert mot in str(e.value) and "SECRET" not in str(e.value)
    s.shutdown()


def test_reponse_bloquee():
    s, _ = serveur(200, {"candidates": []})
    m = modele_gemini("gemini-test", cle="CLE", url_base=f"http://127.0.0.1:{s.server_port}")
    with pytest.raises(ErreurModele):
        m("bonjour")
    s.shutdown()


def test_cle_absente(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.chdir("/tmp")                       # aucun fichier .env ici
    with pytest.raises(ErreurModele):
        modele_gemini("gemini-test")
