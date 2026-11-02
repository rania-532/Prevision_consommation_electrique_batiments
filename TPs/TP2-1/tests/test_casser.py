import pytest

# HEADERS = {"X-API-Key": "test-key"}  # Unnecessary in TP1, necessary in TP2

VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}

SANS_CHARGE = {k: v for k, v in VALID.items() if k != "load_pct"}

CAS_REFUSES = [
    # (description, url, corps, code attendu)
    # 1. Champ manquant
    ("champ manquant", "/v1/predict", SANS_CHARGE, 422),
    # 2. Valeur absurde
    ("valeur absurde", "/v1/predict", {**VALID, "load_pct": 250}, 422),
    # 3. Texte au lieu d'un nombre
    (
        "texte au lieu d'un nombre",
        "/v1/predict",
        {**VALID, "temperature_c": "abc"},
        422,
    ),
    # 4. Champ en trop
    ("champ en trop", "/v1/predict", {**VALID, "unknown_field": 10}, 422),
    # 5. Mauvaise route
    ("mauvaise route", "/v1/predic", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    assert client.post(url, json=corps).status_code == attendu
