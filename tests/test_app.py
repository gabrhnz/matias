import json
import re

import pytest
from fastapi.testclient import TestClient

from app.auth import reset as reset_auth
from app.catalog import lesson_by_id, next_lesson, stats
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    reset_auth()
    yield
    store.reset()
    reset_auth()


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
    assert "Mi progreso" in response.text
    assert "Filtrar por grado" not in response.text
    assert "Sumar con llevadas" in client.get("/modulos/aritmetica").text


def test_filtro_de_sexto_oculta_la_suma(client):
    response = client.get("/modulos/aritmetica?grado=6")
    assert "Problemas de cada día" in response.text
    assert "Sumar con llevadas" not in response.text


def test_la_leccion_no_envia_la_explicacion(client):
    response = client.get("/leccion/sumar-con-llevadas")
    match = re.search(r'id="lesson-data" type="application/json">(.*?)</script>', response.text)
    payload = json.loads(match.group(1))
    assert "explain" not in payload["problems"][0]
    assert "answers" not in payload["problems"][0]
    assert len(payload["problems"]) == 4
    assert "Ver la idea" in response.text


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


def test_fracciones_y_geometria_tienen_figura():
    pie = lesson_by_id("partes-de-un-entero").problems[0]
    shape = lesson_by_id("figuras-planas").problems[0]
    assert pie.scene["type"] == "pie"
    assert pie.scene["filled"] == 1
    assert shape.scene["shape"] == "triangle"
    assert "scene" in __import__("app.catalog", fromlist=["public_problem"]).public_problem(pie)


def test_la_figura_no_cambia_la_respuesta():
    problem = lesson_by_id("perimetro").problems[0]
    assert problem.answers == ("20",)
    assert problem.scene["w"] == 5


def test_pagina_inexistente(client):
    assert client.get("/modulos/no-existe").status_code == 404
    assert client.get("/css/app.css").status_code == 200


def login(client, email="ana@colegio.test", **extra):
    sent = client.post("/api/entrar/codigo", json={"email": email})
    assert sent.status_code == 200
    body = {"email": email, "code": sent.json()["previewCode"], **extra}
    verified = client.post("/api/entrar/verificar", json=body)
    assert verified.status_code == 200
    return verified.json()["student"]


def test_el_codigo_incorrecto_no_entra(client):
    sent = client.post("/api/entrar/codigo", json={"email": "luis@colegio.test"})
    code = sent.json()["previewCode"]
    wrong = "000000" if code != "000000" else "000001"
    bad = client.post("/api/entrar/verificar", json={"email": "luis@colegio.test", "code": wrong})
    assert bad.status_code == 400
    assert client.get("/entrar").status_code == 200


def test_la_racha_sigue_el_dia(client, monkeypatch):
    current = {"day": "2026-11-22"}
    monkeypatch.setattr("app.store.today_iso", lambda: current["day"])
    student = login(client, grade=3)
    lesson = lesson_by_id("sumar-con-llevadas")

    def answer(problem):
        return client.post(
            "/api/comprobar",
            json={
                "lesson_id": lesson.id,
                "problem_id": problem.id,
                "answer": problem.answers[0],
                "student_id": "00000000-0000-4000-8000-000000000099",
            },
        )

    assert answer(lesson.problems[0]).json()["streak"] == 1
    assert answer(lesson.problems[1]).json()["streak"] == 1
    current["day"] = "2026-11-23"
    assert answer(lesson.problems[2]).json()["streak"] == 2
    current["day"] = "2026-11-25"
    assert answer(lesson.problems[3]).json()["streak"] == 1
    progress = client.get(f"/api/progreso/{student['id']}")
    assert progress.json()["student"]["streak"] == 1
    other = client.get("/api/progreso/00000000-0000-4000-8000-000000000099")
    assert other.json()["lessons"] == {}
    page = client.get("/progreso")
    assert "Hola, Ana" in page.text
    assert "ana@colegio.test" in page.text


def test_el_registro_guarda_representante_y_grado(client):
    page = client.get("/entrar")
    assert "Representante" in page.text
    assert "Institución" in page.text
    student = login(
        client,
        grade=3,
        student_name="Ana",
        guardian_name="María Pérez",
        school="Escuela Bolívar",
    )
    assert student["name"] == "Ana"
    assert student["guardian_name"] == "María Pérez"
    assert student["school"] == "Escuela Bolívar"
    assert student["grade"] == 3
    home = client.get("/progreso")
    assert "María Pérez" in home.text
    assert "Escuela Bolívar" in home.text


def test_otro_grado_queda_bloqueado_hasta_que_se_pide(client):
    login(client, grade=3, student_name="Ana", guardian_name="María", school="Escuela Bolívar")
    course = client.get("/modulos/aritmetica")
    assert 'href="/leccion/sumar-con-llevadas"' in course.text
    assert "Problemas de cada día" in course.text
    assert 'href="/leccion/problemas-de-cada-dia"' not in course.text
    blocked = client.get("/leccion/problemas-de-cada-dia")
    assert "Verla igual" in blocked.text
    lesson = lesson_by_id("problemas-de-cada-dia")
    denied = client.post(
        "/api/comprobar",
        json={"lesson_id": lesson.id, "problem_id": lesson.problems[0].id, "answer": "1"},
    )
    assert denied.status_code == 403
    opened = client.get("/leccion/problemas-de-cada-dia?repaso=1")
    assert "Verla igual" not in opened.text
    allowed = client.post(
        "/api/comprobar",
        json={
            "lesson_id": lesson.id,
            "problem_id": lesson.problems[0].id,
            "answer": lesson.problems[0].answers[0],
        },
    )
    assert allowed.status_code == 200
    assert allowed.json()["correct"] is True


def test_el_nombre_se_queda_al_volver_a_entrar(client):
    login(client)
    saved = client.post("/api/perfil", json={"name": "Anita", "grade": 5})
    assert saved.status_code == 200
    assert saved.json()["student"]["name"] == "Anita"
    reset_auth()
    login(client)
    assert "Anita" in client.get("/progreso").text


def _contestar(client, lesson, index, correct, history):
    problem = lesson.problems[index]
    answer = problem.answers[0] if correct else "0"
    if not correct and answer in problem.answers:
        answer = "999"
    return client.post(
        "/api/comprobar",
        json={
            "lesson_id": lesson.id,
            "problem_id": problem.id,
            "answer": answer,
            "history": history,
        },
    )


def test_tres_aciertos_cierran_con_la_mas_dificil(client):
    lesson = lesson_by_id("sumar-con-llevadas")
    page = client.get("/leccion/sumar-con-llevadas")
    assert lesson.problems[2].id in page.text
    first = _contestar(client, lesson, 2, True, [])
    assert first.json()["nextProblemId"] == lesson.problems[0].id
    second = _contestar(
        client,
        lesson,
        0,
        True,
        [{"id": lesson.problems[2].id, "correct": True}],
    )
    assert second.json()["nextProblemId"] == lesson.problems[1].id
    third = _contestar(
        client,
        lesson,
        1,
        True,
        [
            {"id": lesson.problems[2].id, "correct": True},
            {"id": lesson.problems[0].id, "correct": True},
        ],
    )
    assert third.json()["nextProblemId"] == lesson.problems[3].id


def test_dos_errores_siguen_con_una_mas_facil(client):
    lesson = lesson_by_id("sumar-con-llevadas")
    first = _contestar(client, lesson, 2, False, [])
    assert first.json()["correct"] is False
    assert first.json()["nextProblemId"] == lesson.problems[0].id
    second = _contestar(
        client,
        lesson,
        0,
        False,
        [{"id": lesson.problems[2].id, "correct": False}],
    )
    assert second.json()["nextProblemId"] == lesson.problems[1].id
    assert second.json()["explain"]


