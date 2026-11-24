"""MatiLab: servidor FastAPI para Vercel y para el aula local."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.adapt import levels_for, next_index, opening_index
from app.auth import COOKIE, configured, dump_session, read_session, send_code, verify_code
from app.catalog import (
    GRADES,
    first_lesson,
    is_correct,
    lesson_by_id,
    module_by_slug,
    module_of,
    next_lesson,
    problem_in,
    public_problem,
    repertorio,
    stats,
    trial_problem,
    TRIAL,
    visible_lessons,
)
from app.store import clean_grade, clean_label, clean_name, store, valid_student_id

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

app = FastAPI(title="MatiLab", docs_url="/api/docs", redoc_url=None)


class StudentIn(BaseModel):
    student_id: str
    name: str = Field(default="Estudiante", max_length=40)
    grade: int = 4


class HistoryItem(BaseModel):
    id: str = Field(max_length=80)
    correct: bool


class TrialIn(BaseModel):
    problem_id: str = Field(max_length=80)
    answer: str = Field(max_length=40)


class CheckIn(BaseModel):
    lesson_id: str = Field(max_length=80)
    problem_id: str = Field(max_length=80)
    answer: str = Field(max_length=40)
    student_id: str | None = None
    name: str | None = Field(default=None, max_length=40)
    grade: int | None = None
    history: list[HistoryItem] = Field(default_factory=list, max_length=8)


class EmailIn(BaseModel):
    email: str = Field(max_length=120)


class CodeIn(BaseModel):
    email: str = Field(max_length=120)
    code: str = Field(max_length=12)
    guardian_name: str | None = Field(default=None, max_length=60)
    student_name: str | None = Field(default=None, max_length=40)
    grade: int | None = None
    school: str | None = Field(default=None, max_length=80)


class ProfileIn(BaseModel):
    name: str = Field(default="Estudiante", max_length=40)
    grade: int = 4
    guardian_name: str | None = Field(default=None, max_length=60)
    school: str | None = Field(default=None, max_length=80)


def parse_grade(value: str | None) -> int | None:
    if value is None or value in {"", "todos"}:
        return None
    try:
        grade = int(value)
    except ValueError:
        return None
    return grade if grade in GRADES else None


def current_viewer(request: Request) -> dict | None:
    session = read_session(request.cookies.get(COOKIE))
    if not session:
        return None
    student = None
    try:
        student = store.get_progress(session["id"]).get("student")
    except Exception:
        student = None
    viewer = {
        "id": session["id"],
        "email": session.get("email") or "",
        "name": session.get("name") or "Estudiante",
        "grade": session.get("grade") or 4,
        "guardian_name": session.get("guardian_name") or "",
        "school": session.get("school") or "",
        "streak": 0,
    }
    if student:
        viewer["name"] = student.get("name") or viewer["name"]
        viewer["grade"] = student.get("grade") or viewer["grade"]
        viewer["email"] = student.get("email") or viewer["email"]
        viewer["guardian_name"] = student.get("guardian_name") or viewer["guardian_name"]
        viewer["school"] = student.get("school") or viewer["school"]
        viewer["streak"] = int(student.get("streak") or 0)
    return viewer


def render(request: Request, name: str, context: dict, status_code: int = 200):
    grade = context.get("grade")
    payload = {
        "grade": grade,
        "grades": GRADES,
        "grade_qs": f"?grado={grade}" if grade else "",
        "page": context.get("page", ""),
        "grade_action": context.get("grade_action", "/"),
        "numbers": stats(),
        "viewer": current_viewer(request),
        "auth_ready": configured(),
        **context,
    }
    try:
        response = TEMPLATES.TemplateResponse(
            request=request,
            name=name,
            context=payload,
            status_code=status_code,
        )
    except TypeError:
        payload["request"] = request
        response = TEMPLATES.TemplateResponse(name, payload, status_code=status_code)
    return apply_review_cookie(response, request)


def review_on(request: Request) -> bool:
    flag = request.query_params.get("repaso")
    if flag == "1":
        return True
    if flag == "0":
        return False
    return request.cookies.get("matilab_repaso") == "1"


def apply_review_cookie(response, request: Request):
    flag = request.query_params.get("repaso")
    secure = request.url.scheme == "https"
    if flag == "1":
        response.set_cookie(
            "matilab_repaso",
            "1",
            max_age=60 * 60 * 12,
            httponly=False,
            samesite="lax",
            secure=secure,
            path="/",
        )
    elif flag == "0":
        response.delete_cookie("matilab_repaso", path="/")
    return response


def write_session(response, student: dict, secure: bool):
    response.set_cookie(
        COOKIE,
        dump_session(student),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
    return response


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request, grado: str | None = None):
    grade = parse_grade(grado)
    viewer = current_viewer(request)
    start_grade = grade or (viewer["grade"] if viewer else None)
    _module, lesson = first_lesson(start_grade)
    lesson_url = f"/leccion/{lesson.id}" + (f"?grado={grade}" if grade else "")
    return render(
        request,
        "home.html",
        {
            "page": "home",
            "grade": grade,
            "grade_action": "/",
            "modules": repertorio(grade)["modules"],
            "start_url": lesson_url if viewer else "/prueba",
        },
    )


@app.get("/modulos/{slug}", response_class=HTMLResponse)
def course(request: Request, slug: str, grado: str | None = None):
    module = module_by_slug(slug)
    if module is None:
        raise HTTPException(status_code=404)
    viewer = current_viewer(request)
    grade = viewer["grade"] if viewer else parse_grade(grado)
    lessons = module.lessons if viewer else visible_lessons(module, grade)
    others = bool(viewer) and any(grade not in lesson.grades for lesson in lessons)
    return render(
        request,
        "course.html",
        {
            "page": "course",
            "grade": grade if not viewer else None,
            "grade_action": f"/modulos/{module.slug}",
            "module": module,
            "lessons": lessons,
            "repaso": review_on(request) if viewer else False,
            "others": others,
        },
    )


@app.get("/leccion/{lesson_id}", response_class=HTMLResponse)
def lesson_page(request: Request, lesson_id: str, grado: str | None = None):
    lesson = lesson_by_id(lesson_id)
    module = module_of(lesson_id)
    if lesson is None or module is None:
        raise HTTPException(status_code=404)
    viewer = current_viewer(request)
    grade = viewer["grade"] if viewer else parse_grade(grado)
    locked = bool(viewer) and grade not in lesson.grades and not review_on(request)
    nxt = next_lesson(lesson.id, grade)
    payload = {
        "id": lesson.id,
        "title": lesson.title,
        "module": module.slug,
        "moduleTitle": module.title,
        "total": len(lesson.problems),
        "nextId": nxt.id if nxt else None,
        "nextTitle": nxt.title if nxt else None,
        "gradeQs": f"?grado={grade}" if grade else "",
        "problems": [public_problem(problem) for problem in lesson.problems],
        "exampleScene": lesson.example_scene,
        "startProblemId": lesson.problems[opening_index(levels_for(len(lesson.problems)))].id,
        "passScore": 75,
        "moduleLessonIds": [item.id for item in (visible_lessons(module, grade) if grade else module.lessons)],
    }
    return render(
        request,
        "lesson.html",
        {
            "page": "lesson",
            "grade": grade,
            "grade_action": f"/modulos/{module.slug}",
            "module": module,
            "lesson": lesson,
            "payload": payload,
            "locked": locked,
        },
    )


@app.get("/progreso", response_class=HTMLResponse)
def progress_page(request: Request, grado: str | None = None):
    grade = parse_grade(grado)
    return render(
        request,
        "progress.html",
        {
            "page": "progress",
            "grade": grade,
            "grade_action": "/progreso",
            "modules": repertorio(None)["modules"],
        },
    )


@app.get("/conocenos", response_class=HTMLResponse)
def about_page(request: Request):
    return render(request, "about.html", {"page": "about", "grade": None})


@app.get("/prueba", response_class=HTMLResponse)
def trial_page(request: Request):
    viewer = current_viewer(request)
    if viewer:
        _module, lesson = first_lesson(viewer["grade"])
        return RedirectResponse(f"/leccion/{lesson.id}", status_code=303)
    return render(
        request,
        "prueba.html",
        {
            "page": "trial",
            "grade": None,
            "problems": [public_problem(problem) for problem in TRIAL],
        },
    )


@app.post("/api/prueba")
def check_trial(body: TrialIn):
    if not body.answer.strip():
        raise HTTPException(status_code=400, detail="Elige una respuesta")
    problem = trial_problem(body.problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="No encontramos esa práctica")
    correct = is_correct(problem, body.answer)
    return {"correct": correct, "explain": problem.explain if correct else ""}


@app.get("/entrar", response_class=HTMLResponse)
def enter_page(request: Request):
    if read_session(request.cookies.get(COOKIE)):
        return RedirectResponse("/progreso", status_code=303)
    return render(request, "entrar.html", {"page": "enter", "grade": None})


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    return FileResponse(PUBLIC_DIR / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/salud")
def health():
    return {
        "ok": True,
        "name": "MatiLab",
        "storage": "supabase" if store.enabled else "local",
        "auth": "supabase" if configured() else "local",
        **stats(),
    }


@app.get("/api/repertorio")
def api_catalog(grado: str | None = None):
    return repertorio(parse_grade(grado))


@app.get("/api/yo")
def me(request: Request):
    session = read_session(request.cookies.get(COOKIE))
    if not session:
        return {"student": None, "lessons": {}, "storage": "local"}
    if not valid_student_id(session.get("id")):
        raise HTTPException(status_code=401, detail="Entra otra vez")
    data = store.get_progress(session["id"])
    student = data.get("student") or {
        "id": session["id"],
        "name": session.get("name") or "Estudiante",
        "grade": session.get("grade") or 4,
        "email": session.get("email") or None,
        "guardian_name": session.get("guardian_name") or "",
        "school": session.get("school") or "",
        "streak": 0,
    }
    return {
        "student": student,
        "lessons": data.get("lessons") or {},
        "storage": data.get("storage"),
        "degraded": data.get("degraded", False),
    }


@app.post("/api/entrar/codigo")
def request_code(body: EmailIn):
    try:
        return send_code(body.email)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail="No pudimos enviar el código. Revisa el correo e inténtalo otra vez.",
        ) from error


@app.post("/api/entrar/verificar")
def confirm_code(request: Request, body: CodeIn):
    profile = None
    if any(value is not None for value in (body.student_name, body.guardian_name, body.school)):
        if (
            not clean_label(body.guardian_name)
            or not clean_label(body.school, 80)
            or not (body.student_name or "").strip()
            or body.grade not in GRADES
        ):
            raise HTTPException(status_code=400, detail="Completa el registro")
        profile = {
            "guardian_name": body.guardian_name,
            "student_name": body.student_name,
            "grade": body.grade,
            "school": body.school,
        }
    elif body.grade is not None:
        profile = {"grade": body.grade}
    try:
        student = verify_code(body.email, body.code, profile)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail="No pudimos comprobar el código.") from error
    response = JSONResponse({"ok": True, "student": student})
    return write_session(response, student, request.url.scheme == "https")


@app.post("/api/salir")
def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie(COOKIE, path="/")
    return response


@app.post("/api/perfil")
def save_profile(request: Request, body: ProfileIn):
    session = read_session(request.cookies.get(COOKIE))
    if not session or not valid_student_id(session.get("id")):
        raise HTTPException(status_code=401, detail="Entra con tu correo")
    try:
        saved = store.upsert_student(
            session["id"],
            body.name,
            body.grade,
            email=session.get("email") or None,
            guardian_name=body.guardian_name,
            school=body.school,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    response = JSONResponse(saved)
    return write_session(response, saved["student"], request.url.scheme == "https")


@app.post("/api/estudiantes")
def save_student(body: StudentIn):
    if not valid_student_id(body.student_id):
        raise HTTPException(status_code=400, detail="El código del estudiante no es válido")
    try:
        return store.upsert_student(body.student_id, body.name, body.grade)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/progreso/{student_id}")
def read_progress(student_id: str):
    if not valid_student_id(student_id):
        raise HTTPException(status_code=400, detail="El código del estudiante no es válido")
    try:
        return store.get_progress(student_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _next_problem_id(lesson, history, current_id: str, correct: bool) -> str | None:
    ids = [problem.id for problem in lesson.problems]
    if current_id not in ids:
        return None
    shown: list[int] = []
    results: list[bool] = []
    for item in history:
        if item.id not in ids or item.id == current_id or ids.index(item.id) in shown:
            continue
        shown.append(ids.index(item.id))
        results.append(item.correct)
    shown.append(ids.index(current_id))
    results.append(correct)
    nxt = next_index(levels_for(len(ids)), shown, results)
    if nxt is None:
        return None
    return ids[nxt]


@app.post("/api/comprobar")
def check_answer(request: Request, body: CheckIn):
    if not body.answer.strip():
        raise HTTPException(status_code=400, detail="Escribe una respuesta")
    lesson = lesson_by_id(body.lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="No encontramos esa lección")
    problem = problem_in(lesson, body.problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="No encontramos esa práctica")
    session = read_session(request.cookies.get(COOKIE))
    if (
        session
        and valid_student_id(session.get("id"))
        and session.get("grade") not in lesson.grades
        and request.cookies.get("matilab_repaso") != "1"
    ):
        raise HTTPException(status_code=403, detail="Esta lección no está en tu grado")
    correct = is_correct(problem, body.answer)
    result = {
        "correct": correct,
        "explain": problem.explain,
        "hint": problem.hint,
        "persisted": False,
        "storage": "local",
        "nextProblemId": _next_problem_id(lesson, body.history, problem.id, correct),
    }
    student_id = None
    name = body.name
    grade = body.grade
    if session and valid_student_id(session.get("id")):
        student_id = session["id"]
        name = session.get("name")
        grade = session.get("grade")
    elif body.student_id:
        if not valid_student_id(body.student_id):
            raise HTTPException(status_code=400, detail="El código del estudiante no es válido")
        student_id = body.student_id
    if student_id:
        saved = store.record(
            student_id,
            clean_name(name),
            clean_grade(grade),
            lesson.id,
            problem.id,
            correct,
        )
        result["persisted"] = True
        result["storage"] = saved["storage"]
        result["degraded"] = saved["degraded"]
        result["progress"] = saved["lesson"]
        result["streak"] = saved["streak"]
    return result


@app.exception_handler(404)
async def not_found(request: Request, _exc: HTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "No encontrado"}, status_code=404)
    return render(request, "404.html", {"page": "missing", "grade": None}, status_code=404)


if not os.getenv("VERCEL"):
    app.mount("/css", StaticFiles(directory=PUBLIC_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=PUBLIC_DIR / "js"), name="js")
    app.mount("/img", StaticFiles(directory=PUBLIC_DIR / "img"), name="img")
