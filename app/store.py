"""Progreso del estudiante.

Si existen SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY, el progreso se guarda en
Postgres. Si no, se guarda en la memoria de este proceso. El navegador además
conserva una copia, así la práctica no se pierde al recargar.
"""

from __future__ import annotations

import logging
import os
import re
import threading
from datetime import datetime, timezone

import httpx

from app.catalog import lesson_by_id

logger = logging.getLogger("matilab")

_UUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def valid_student_id(value: str | None) -> bool:
    return bool(value and _UUID.match(value))


def clean_name(name: str | None) -> str:
    if not name:
        return "Estudiante"
    cleaned = " ".join(name.split())
    cleaned = "".join(char for char in cleaned if char.isprintable())
    return cleaned[:40] or "Estudiante"


def clean_grade(grade: int | None) -> int:
    return grade if grade in (3, 4, 5, 6) else 4


class Store:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.students: dict[str, dict] = {}
        self.progress: dict[str, dict[str, dict]] = {}
        self._client = httpx.Client(timeout=8.0)

    @property
    def supabase_url(self) -> str:
        return os.environ.get("SUPABASE_URL", "").strip().rstrip("/")

    @property
    def supabase_key(self) -> str:
        return os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def reset(self) -> None:
        with self.lock:
            self.students.clear()
            self.progress.clear()

    def upsert_student(self, student_id: str, name: str | None, grade: int | None) -> dict:
        if not valid_student_id(student_id):
            raise ValueError("El código del estudiante no es válido")
        student = {
            "id": student_id,
            "name": clean_name(name),
            "grade": clean_grade(grade),
        }
        if self.enabled:
            try:
                self._upsert_remote_student(student)
                with self.lock:
                    self.students[student_id] = student
                return {"student": student, "storage": "supabase", "degraded": False}
            except Exception:
                logger.warning("Supabase no guardó al estudiante; se usa el modo local")
        with self.lock:
            self.students[student_id] = student
        return {"student": student, "storage": "local", "degraded": self.enabled}

    def record(
        self,
        student_id: str,
        name: str | None,
        grade: int | None,
        lesson_id: str,
        problem_id: str,
        correct: bool,
    ) -> dict:
        lesson = lesson_by_id(lesson_id)
        if lesson is None or not any(problem.id == problem_id for problem in lesson.problems):
            raise ValueError("La práctica no existe")
        self.upsert_student(student_id, name, grade)
        if self.enabled:
            try:
                state = self._record_remote(student_id, lesson_id, problem_id, correct)
                return {"lesson": state, "storage": "supabase", "degraded": False}
            except Exception:
                logger.warning("Supabase no guardó el progreso; se usa el modo local")
        state = self._record_memory(student_id, lesson_id, problem_id, correct)
        return {"lesson": state, "storage": "local", "degraded": self.enabled}

    def get_progress(self, student_id: str) -> dict:
        if not valid_student_id(student_id):
            raise ValueError("El código del estudiante no es válido")
        if self.enabled:
            try:
                return self._read_remote(student_id) | {"storage": "supabase", "degraded": False}
            except Exception:
                logger.warning("Supabase no devolvió el progreso; se usa el modo local")
        with self.lock:
            student = self.students.get(student_id)
            raw = self.progress.get(student_id, {})
        lessons = {
            lesson_id: self._shape(lesson_id, set(row.get("solved") or []), set(row.get("correct") or []))
            for lesson_id, row in raw.items()
        }
        return {
            "student": student,
            "lessons": lessons,
            "storage": "local",
            "degraded": self.enabled,
        }

    def _record_memory(self, student_id: str, lesson_id: str, problem_id: str, correct: bool) -> dict:
        with self.lock:
            bucket = self.progress.setdefault(student_id, {})
            current = bucket.get(lesson_id, {"solved": [], "correct": []})
            solved = set(current["solved"])
            right = set(current["correct"])
            solved.add(problem_id)
            if correct:
                right.add(problem_id)
            state = self._shape(lesson_id, solved, right)
            bucket[lesson_id] = {"solved": state["solved"], "correct": state["correct"]}
            return state

    def _shape(self, lesson_id: str, solved: set[str], correct: set[str]) -> dict:
        lesson = lesson_by_id(lesson_id)
        order = [problem.id for problem in lesson.problems] if lesson else []
        known = set(order)
        solved_list = [problem_id for problem_id in order if problem_id in solved and problem_id in known]
        correct_list = [problem_id for problem_id in order if problem_id in correct and problem_id in known]
        total = len(order)
        return {
            "lesson_id": lesson_id,
            "solved": solved_list,
            "correct": correct_list,
            "completed": total > 0 and len(solved_list) >= total,
            "total": total,
        }

    def _headers(self, prefer: str) -> dict[str, str]:
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        }

    def _request(self, method: str, path: str, body: object | None = None, prefer: str = "return=representation"):
        response = self._client.request(
            method,
            f"{self.supabase_url}{path}",
            headers=self._headers(prefer),
            json=body,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Supabase respondió {response.status_code}")
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def _upsert_remote_student(self, student: dict) -> None:
        self._request(
            "POST",
            "/rest/v1/students?on_conflict=id",
            {
                "id": student["id"],
                "display_name": student["name"],
                "grade": student["grade"],
            },
            prefer="resolution=merge-duplicates,return=minimal",
        )

    def _record_remote(self, student_id: str, lesson_id: str, problem_id: str, correct: bool) -> dict:
        rows = self._request(
            "GET",
            f"/rest/v1/lesson_progress?student_id=eq.{student_id}&lesson_id=eq.{lesson_id}&select=solved,correct",
        ) or []
        solved = set(rows[0].get("solved") or []) if rows else set()
        right = set(rows[0].get("correct") or []) if rows else set()
        solved.add(problem_id)
        if correct:
            right.add(problem_id)
        state = self._shape(lesson_id, solved, right)
        self._request(
            "POST",
            "/rest/v1/lesson_progress?on_conflict=student_id,lesson_id",
            {
                "student_id": student_id,
                "lesson_id": lesson_id,
                "solved": state["solved"],
                "correct": state["correct"],
                "completed": state["completed"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            prefer="resolution=merge-duplicates,return=minimal",
        )
        return state

    def _read_remote(self, student_id: str) -> dict:
        students = self._request(
            "GET",
            f"/rest/v1/students?id=eq.{student_id}&select=id,display_name,grade",
        ) or []
        rows = self._request(
            "GET",
            f"/rest/v1/lesson_progress?student_id=eq.{student_id}&select=lesson_id,solved,correct",
        ) or []
        lessons = {}
        for row in rows:
            state = self._shape(row["lesson_id"], set(row.get("solved") or []), set(row.get("correct") or []))
            lessons[row["lesson_id"]] = {"solved": state["solved"], "correct": state["correct"], "completed": state["completed"]}
        student = None
        if students:
            student = {
                "id": students[0]["id"],
                "name": students[0]["display_name"],
                "grade": students[0]["grade"],
            }
        return {"student": student, "lessons": lessons}


store = Store()
