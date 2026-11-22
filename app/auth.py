"""Ingreso con un código al correo.

Con Supabase conectado, el código lo envía Supabase Auth.
Sin esas claves, el código aparece en la respuesta para poder practicar el flujo.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time

import httpx

from app.store import clean_name, store

logger = logging.getLogger("matilab")

COOKIE = "matilab_sesion"
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_pending: dict[str, dict] = {}
_sent_at: dict[str, float] = {}
_client = httpx.Client(timeout=8.0)


def reset() -> None:
    _pending.clear()
    _sent_at.clear()


def configured() -> bool:
    return bool(_url() and _key())


def normalize_email(value: str | None) -> str:
    email = (value or "").strip().lower()
    if len(email) > 120 or not _EMAIL.match(email):
        raise ValueError("Escribe un correo válido")
    return email


def name_from_email(email: str) -> str:
    local = email.split("@", 1)[0].replace(".", " ").replace("_", " ").replace("-", " ")
    words = [part.capitalize() for part in local.split() if part]
    return clean_name(" ".join(words))


def send_code(email: str) -> dict:
    email = normalize_email(email)
    now = time.time()
    if now - _sent_at.get(email, 0) < 30:
        raise ValueError("Espera un momento y pide otro código")
    if configured():
        _send_remote(email)
        _sent_at[email] = now
        return {"ok": True, "delivery": "email"}
    code = f"{secrets.randbelow(1_000_000):06d}"
    _pending[email] = {"code": code, "exp": now + 600, "tries": 0}
    _sent_at[email] = now
    return {"ok": True, "delivery": "local", "previewCode": code}


def verify_code(email: str, raw_code: str, profile: dict | None = None) -> dict:
    email = normalize_email(email)
    code = "".join(char for char in (raw_code or "") if char.isdigit())
    if len(code) < 6 or len(code) > 10:
        raise ValueError("Escribe el código del correo")
    if configured():
        user_id = _verify_remote(email, code)
        student = store.account_for_email(email, name_from_email(email), preferred_id=user_id)
    else:
        _verify_local(email, code)
        student = store.account_for_email(email, name_from_email(email))
    if not profile:
        return student
    grade = profile.get("grade")
    return store.upsert_student(
        student["id"],
        profile.get("student_name") or student.get("name"),
        grade if grade in (3, 4, 5, 6) else student.get("grade"),
        email=email,
        guardian_name=profile.get("guardian_name"),
        school=profile.get("school"),
    )["student"]


def read_session(cookie: str | None) -> dict | None:
    return _unsign(cookie)


def dump_session(student: dict) -> str:
    payload = {
        "id": student["id"],
        "email": student.get("email") or "",
        "name": student.get("name") or "Estudiante",
        "grade": student.get("grade") or 4,
        "guardian_name": student.get("guardian_name") or "",
        "school": student.get("school") or "",
        "exp": int(time.time()) + 60 * 60 * 24 * 30,
    }
    return _sign(payload)


def _sign(payload: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def _unsign(token: str | None) -> dict | None:
    if not token or "." not in token:
        return None
    body, signature = token.rsplit(".", 1)
    expected = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("exp", 0) < time.time():
        return None
    if not data.get("id"):
        return None
    return data


def _secret() -> bytes:
    raw = (
        os.environ.get("MATILAB_SECRET", "").strip()
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or "matilab-desarrollo-local"
    )
    return raw.encode()


def _url() -> str:
    return os.environ.get("SUPABASE_URL", "").strip().rstrip("/")


def _key() -> str:
    return os.environ.get("SUPABASE_ANON_KEY", "").strip() or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()


def _auth_headers() -> dict[str, str]:
    key = _key()
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _send_remote(email: str) -> None:
    try:
        response = _client.post(
            f"{_url()}/auth/v1/otp",
            headers=_auth_headers(),
            json={"email": email, "create_user": True},
        )
    except httpx.HTTPError as error:
        logger.warning("Supabase Auth no respondió al enviar el código")
        raise RuntimeError("correo") from error
    if response.status_code >= 400:
        logger.warning("Supabase Auth rechazó el envío: %s", response.status_code)
        raise RuntimeError("correo")


def _verify_remote(email: str, code: str) -> str:
    try:
        response = _client.post(
            f"{_url()}/auth/v1/verify",
            headers=_auth_headers(),
            json={"type": "email", "email": email, "token": code},
        )
    except httpx.HTTPError as error:
        logger.warning("Supabase Auth no respondió al verificar")
        raise RuntimeError("codigo") from error
    if response.status_code >= 400:
        raise ValueError("Ese código no coincide")
    user = (response.json() or {}).get("user") or {}
    user_id = user.get("id")
    if not user_id:
        raise RuntimeError("codigo")
    return user_id


def _verify_local(email: str, code: str) -> None:
    pending = _pending.get(email)
    if not pending or pending["exp"] < time.time():
        _pending.pop(email, None)
        raise ValueError("Ese código ya no sirve. Pide otro")
    pending["tries"] += 1
    if pending["tries"] > 5:
        _pending.pop(email, None)
        raise ValueError("Pide otro código")
    if not hmac.compare_digest(pending["code"], code):
        raise ValueError("Ese código no coincide")
    _pending.pop(email, None)
