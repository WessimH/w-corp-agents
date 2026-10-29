import asyncio
import json
from types import SimpleNamespace

import server
import sf


def message_outil(monkeypatch, payload, outil, arguments):
    monkeypatch.setattr(sf.subprocess, "run", lambda cmd, **kw: SimpleNamespace(stdout=json.dumps(payload)))
    try:
        resultat = asyncio.run(server.mcp.call_tool(outil, arguments))
        return " ".join(getattr(c, "text", "") for c in resultat.content)
    except Exception as e:  # depending on the SDK version, the tool error may surface as an exception
        return str(e)


def test_session_expiree_atteint_le_modele(monkeypatch):
    texte = message_outil(monkeypatch, {"status": 1, "message": "expired access/refresh token"},
                          "soql", {"query": "SELECT Id FROM Account"})
    assert "sf org login web -a" in texte


def test_erreur_soql_atteint_le_modele(monkeypatch):
    texte = message_outil(monkeypatch, {"status": 1, "message": "MALFORMED_QUERY: unexpected token"},
                          "soql", {"query": "SELEC Id"})
    assert "MALFORMED_QUERY" in texte
