import json
from types import SimpleNamespace

import pytest

import sf


def fake_run(monkeypatch, payload):
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return SimpleNamespace(stdout=json.dumps(payload), returncode=payload.get("status", 0))

    monkeypatch.setattr(sf.subprocess, "run", run)
    return calls


def test_commande_sans_shell(monkeypatch):
    calls = fake_run(monkeypatch, {"status": 0, "result": {}})
    sf.run_sf(["sobject", "describe", "--sobject", "Account; rm -rf /"])
    cmd, kwargs = calls[0]
    assert cmd == ["sf", "sobject", "describe", "--sobject", "Account; rm -rf /",
                   "--target-org", sf.TARGET_ORG, "--json"]
    assert kwargs.get("shell") is not True


def test_erreur_sf_levee(monkeypatch):
    fake_run(monkeypatch, {"status": 1, "message": "INVALID_TYPE: sObject type 'Acount' is not supported"})
    with pytest.raises(sf.SfError, match="INVALID_TYPE"):
        sf.run_sf(["sobject", "describe", "--sobject", "Acount"])


def test_session_expiree_donne_la_commande(monkeypatch):
    fake_run(monkeypatch, {"status": 1, "message": "Error authenticating with the refresh token due to: expired access/refresh token"})
    with pytest.raises(sf.SfError, match="sf org login web -a"):
        sf.run_sf(["data", "query", "--query", "SELECT Id FROM Account"])


def test_trim_describe_garde_l_essentiel():
    champ = {f"cle{i}": i for i in range(24)}
    champ.update(name="Name", label="Nom", type="string", length=255,
                 nillable=False, createable=True, defaultedOnCreate=False, referenceTo=[])
    [resultat] = sf.trim_describe({"fields": [champ]})
    assert set(resultat) == {"name", "label", "type", "length", "required", "referenceTo"}
    assert resultat["required"] is True


def test_trim_query_plafonne_et_nettoie():
    records = [{"attributes": {"type": "Account"}, "Id": str(i),
                "Owner": {"attributes": {"type": "User"}, "Name": "X"}} for i in range(250)]
    resultat = sf.trim_query({"totalSize": 250, "records": records})
    assert len(resultat["records"]) == 200
    assert resultat["truncated"] is True
    assert resultat["records"][0]["Owner"] == {"Name": "X"}
    assert "attributes" not in resultat["records"][0]


# Real sf 2.155 output for a failed validation (captured on a sandbox, 'stack' field removed).
ECHEC_VALIDATION = {
    "name": "FailedValidationError", "status": 1, "data": {"deployId": "0Afbd00000BpsknCAB"},
    "message": "Failed to validate the deployment (0Afbd00000BpsknCAB). Due To:\n"
               "Error in Zz_Inexistant__c.Bad__c - Entity 'Zz_Inexistant__c' not found. (3:13)\n"
               "Error in Flow.Reminder - The version of the flow is invalid.\n\n2 component error(s)",
}


def test_validation_en_echec_liste_les_erreurs(monkeypatch):
    fake_run(monkeypatch, ECHEC_VALIDATION)
    resultat = sf.trim_validate(sf.run_sf(["project", "deploy", "validate"], allow_failure=True))
    assert resultat["success"] is False
    assert resultat["errors"] == [
        {"file": "Zz_Inexistant__c.Bad__c", "problem": "Entity 'Zz_Inexistant__c' not found.", "line": 3},
        {"file": "Flow.Reminder", "problem": "The version of the flow is invalid.", "line": None},
    ]


# Apex test failure on a sandbox (sf 2.155, excerpt): no "Error in" line.
ECHEC_TESTS = {
    "name": "FailedValidationError", "status": 1, "data": {"deployId": "0Afbd00000BrFozCAF"},
    "message": "Failed to validate the deployment (0Afbd00000BrFozCAF). Due To:\n"
               "Average test coverage across all Apex Classes and Triggers is 69%, "
               "at least 75% test coverage is required.\n\n\n"
               "InvoiceTest.testUpsert - System.DmlException: Upsert failed.",
}


def test_echec_sans_ligne_reconnue_rend_le_texte_brut(monkeypatch):
    fake_run(monkeypatch, ECHEC_TESTS)
    resultat = sf.trim_validate(sf.run_sf(["project", "deploy", "validate"], allow_failure=True))
    assert resultat["success"] is False
    [erreur] = resultat["errors"]
    assert erreur["problem"].startswith("Average test coverage")
    assert "InvoiceTest.testUpsert" in erreur["problem"]


def test_validation_reussie(monkeypatch):
    fake_run(monkeypatch, {"status": 0, "result": {"success": True, "id": "0Af"}})
    resultat = sf.trim_validate(sf.run_sf(["project", "deploy", "validate"], allow_failure=True))
    assert resultat == {"success": True, "errors": []}


def test_validation_session_expiree_leve_quand_meme(monkeypatch):
    fake_run(monkeypatch, {"status": 1, "name": "AuthError", "message": "expired access/refresh token"})
    with pytest.raises(sf.SfError, match="sf org login web -a"):
        sf.run_sf(["project", "deploy", "validate"], allow_failure=True)
