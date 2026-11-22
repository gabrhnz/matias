import json
import re

import pytest
from fastapi.testclient import TestClient

from app.catalog import lesson_by_id, next_lesson, stats
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    yield
    store.reset()


@pytest.fixture()
def client():
    return TestClient(app)


def test_repertorio_tiene_cuatro_modulos():
    data = stats()
    assert data == {"modules": 4, "lessons": 32, "problems": 128}


def test_siguiente_leccion_respeta_el_grado():
    assert next_lesson("sumar-con-llevadas").id == "restar-con-prestado"
    assert next_lesson("sumar-con-llevadas", 6).id == "problemas-de-cada-dia"


def test_inicio_muestra_el_repertorio(client):
    response = client.get("/")
    assert response.status_code == 200
    for title in ("Aritmética", "Fracciones", "Geometría", "Razonamiento lógico"):
        assert title in response.text
    assert "Sumar con llevadas" in response.text


def test_filtro_de_sexto_oculta_la_suma(client):
    response = client.get("/?grado=6")
    assert "Problemas de cada día" in response.text
    assert "Sumar con llevadas" not in response.text


def test_la_leccion_no_envia_la_explicacion(client):
    response = client.get("/leccion/sumar-con-llevadas")
    match = re.search(r'id="lesson-data" type="application/json">(.*?)</script>', response.text)
    payload = json.loads(match.group(1))
    assert "explain" not in payload["problems"][0]
    assert "answers" not in payload["problems"][0]
    assert len(payload["problems"]) == 4


def test_comprobar_correcto_e_incorrecto(client):
    lesson = lesson_by_id("sumar-con-llevadas")
    problem = lesson.problems[0]
    student = {
        "student_id": "11111111-1111-4111-8111-111111111111",
        "name": "Ana",
        "grade": 3,
    }
    wrong = client.post("/api/comprobar", json={**student, "lesson_id": lesson.id, "problem_id": problem.id, "answer": "32"})
    assert wrong.status_code == 200
    assert wrong.json()["correct"] is False
    assert problem.id in wrong.json()["progress"]["solved"]
    assert problem.id not in wrong.json()["progress"]["correct"]

    right = client.post(
        "/api/comprobar",
        json={**student, "lesson_id": lesson.id, "problem_id": problem.id, "answer": problem.answers[0]},
    )
    assert right.json()["correct"] is True
    assert problem.id in right.json()["progress"]["correct"]
    assert right.json()["progress"]["completed"] is False


def test_la_leccion_se_completa_al_responder_todas(client):
    lesson = lesson_by_id("sumar-con-llevadas")
    student = "22222222-2222-4222-8222-222222222222"
    last = None
    for problem in lesson.problems:
        last = client.post(
            "/api/comprobar",
            json={
                "student_id": student,
                "name": "Luis",
                "grade": 3,
                "lesson_id": lesson.id,
                "problem_id": problem.id,
                "answer": problem.answers[0],
            },
        )
    assert last.json()["progress"]["completed"] is True
    progress = client.get(f"/api/progreso/{student}")
    assert progress.json()["lessons"][lesson.id]["completed"] is True


def test_fraccion_acepta_equivalente(client):
    response = client.post(
        "/api/comprobar",
        json={"lesson_id": "sumar-fracciones", "problem_id": "sumar-fracciones-p3", "answer": "1/2"},
    )
    assert response.json()["correct"] is True


def test_pagina_inexistente(client):
    assert client.get("/modulos/no-existe").status_code == 404
    assert client.get("/css/app.css").status_code == 200
