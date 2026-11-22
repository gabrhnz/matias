"""MatiLab: servidor FastAPI para Vercel y para el aula local."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

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
    visible_lessons,
)
from app.store import clean_grade, clean_name, store, valid_student_id

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

app = FastAPI(title="MatiLab", docs_url="/api/docs", redoc_url=None)


class StudentIn(BaseModel):
    student_id: str
    name: str = Field(default="Estudiante", max_length=40)
    grade: int = 4


class CheckIn(BaseModel):
    lesson_id: str = Field(max_length=80)
    problem_id: str = Field(max_length=80)
    answer: str = Field(max_length=40)
    student_id: str | None = None
    name: str | None = Field(default=None, max_length=40)
    grade: int | None = None


def parse_grade(value: str | None) -> int | None:
    if value is None or value in {"", "todos"}:
        return None
    try:
        grade = int(value)
    except ValueError:
        return None
    return grade if grade in GRADES else None


def render(request: Request, name: str, context: dict, status_code: int = 200):
    grade = context.get("grade")
    payload = {
        "grade": grade,
        "grades": GRADES,
        "grade_qs": f"?grado={grade}" if grade else "",
        "page": context.get("page", ""),
        "grade_action": context.get("grade_action", "/"),
        "numbers": stats(),
        **context,
    }
    try:
        return TEMPLATES.TemplateResponse(
            request=request,
            name=name,
            context=payload,
            status_code=status_code,
        )
    except TypeError:
        payload["request"] = request
        return TEMPLATES.TemplateResponse(name, payload, status_code=status_code)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request, grado: str | None = None):
    grade = parse_grade(grado)
    module, lesson = first_lesson(grade)
    modules = []
    for item in repertorio(grade)["modules"]:
        modules.append(item)
    return render(
        request,
        "home.html",
        {
            "page": "home",
            "grade": grade,
            "grade_action": "/",
            "modules": modules,
            "start_url": f"/leccion/{lesson.id}" + (f"?grado={grade}" if grade else ""),
            "start_title": lesson.title,
            "start_module": module.title,
        },
    )


@app.get("/modulos/{slug}", response_class=HTMLResponse)
def course(request: Request, slug: str, grado: str | None = None):
    module = module_by_slug(slug)
    if module is None:
        raise HTTPException(status_code=404)
    grade = parse_grade(grado)
    lessons = visible_lessons(module, grade)
    return render(
        request,
        "course.html",
        {
            "page": "course",
            "grade": grade,
            "grade_action": f"/modulos/{module.slug}",
            "module": module,
            "lessons": lessons,
        },
    )


@app.get("/leccion/{lesson_id}", response_class=HTMLResponse)
def lesson_page(request: Request, lesson_id: str, grado: str | None = None):
    lesson = lesson_by_id(lesson_id)
    module = module_of(lesson_id)
    if lesson is None or module is None:
        raise HTTPException(status_code=404)
    grade = parse_grade(grado)
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


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    return FileResponse(PUBLIC_DIR / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/salud")
def health():
    return {
        "ok": True,
        "name": "MatiLab",
        "storage": "supabase" if store.enabled else "local",
        **stats(),
    }


@app.get("/api/repertorio")
def api_catalog(grado: str | None = None):
    return repertorio(parse_grade(grado))


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


@app.post("/api/comprobar")
def check_answer(body: CheckIn):
    if not body.answer.strip():
        raise HTTPException(status_code=400, detail="Escribe una respuesta")
    lesson = lesson_by_id(body.lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="No encontramos esa lección")
    problem = problem_in(lesson, body.problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="No encontramos esa práctica")
    correct = is_correct(problem, body.answer)
    result = {
        "correct": correct,
        "explain": problem.explain,
        "hint": problem.hint,
        "persisted": False,
        "storage": "local",
    }
    if body.student_id:
        if not valid_student_id(body.student_id):
            raise HTTPException(status_code=400, detail="El código del estudiante no es válido")
        saved = store.record(
            body.student_id,
            clean_name(body.name),
            clean_grade(body.grade),
            lesson.id,
            problem.id,
            correct,
        )
        result["persisted"] = True
        result["storage"] = saved["storage"]
        result["degraded"] = saved["degraded"]
        result["progress"] = saved["lesson"]
    return result


@app.exception_handler(404)
async def not_found(request: Request, _exc: HTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "No encontrado"}, status_code=404)
    return render(request, "404.html", {"page": "missing", "grade": None}, status_code=404)


if not os.getenv("VERCEL"):
    app.mount("/css", StaticFiles(directory=PUBLIC_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=PUBLIC_DIR / "js"), name="js")
