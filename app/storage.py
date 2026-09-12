from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "data" / "nourishai.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT '',
                goal TEXT NOT NULL DEFAULT '',
                plan_json TEXT NOT NULL,
                meta_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_saved_plans_user_id
            ON saved_plans(user_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS reset_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_reset_requests_user
            ON reset_requests(user_id, created_at DESC);
            """
        )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=64,
    )
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n, r, p, salt_hex, digest_hex = encoded.split("$")
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(bytes.fromhex(digest_hex)),
        )
        return secrets.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    return all(
        [
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ]
    )


def create_user(name: str, email: str, password: str) -> dict[str, Any]:
    name = " ".join(name.strip().split())
    email = email.strip().lower()
    if not name:
        raise ValueError("Please enter your full name.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Please enter a valid email address.")
    if not validate_password_strength(password):
        raise ValueError("Password does not meet the required strength.")
    now = _now().isoformat()
    encoded = _hash_password(password)
    try:
        with _connect() as conn:
            cur = conn.execute(
                "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
                (name, email, encoded, now),
            )
            user_id = cur.lastrowid
    except sqlite3.IntegrityError as exc:
        raise ValueError("An account with this email already exists.") from exc
    return {"id": int(user_id), "name": name, "email": email}


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    email = email.strip().lower()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id,name,email,password_hash FROM users WHERE email=?",
            (email,),
        ).fetchone()
    if not row or not _verify_password(password, row["password_hash"]):
        return None
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def update_password(user_id: int, password: str) -> None:
    encoded = _hash_password(password)
    with _connect() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (encoded, user_id))


def save_plan_for_user(user_id: int, title: str, plan: dict[str, Any], meta: dict[str, Any]) -> int:
    import json

    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO saved_plans(user_id,title,country,goal,plan_json,meta_json,created_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                user_id,
                title,
                str(meta.get("country", "")),
                str(meta.get("goal", "")),
                json.dumps(plan, ensure_ascii=False),
                json.dumps(meta, ensure_ascii=False),
                _now().strftime("%Y-%m-%d %H:%M UTC"),
            ),
        )
        return int(cur.lastrowid)


def list_saved_plans(user_id: int) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id,title,country,goal,created_at FROM saved_plans WHERE user_id=? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_saved_plan(plan_id: int, user_id: int) -> dict[str, Any] | None:
    import json

    with _connect() as conn:
        row = conn.execute(
            "SELECT id,title,plan_json,meta_json FROM saved_plans WHERE id=? AND user_id=?",
            (plan_id, user_id),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "plan": json.loads(row["plan_json"]),
        "meta": json.loads(row["meta_json"]),
    }


def delete_saved_plan(plan_id: int, user_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM saved_plans WHERE id=? AND user_id=?", (plan_id, user_id))


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def create_reset_request(email: str) -> dict[str, Any] | None:
    email = email.strip().lower()
    with _connect() as conn:
        user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            return None
        code = f"{secrets.randbelow(10**8):08d}"
        created = _now()
        expires = created + timedelta(minutes=30)
        conn.execute("UPDATE reset_requests SET used=1 WHERE user_id=? AND used=0", (user["id"],))
        cur = conn.execute(
            """
            INSERT INTO reset_requests(user_id,code_hash,expires_at,used,created_at)
            VALUES(?,?,?,?,?)
            """,
            (user["id"], _hash_code(code), expires.isoformat(), 0, created.isoformat()),
        )
        return {"id": int(cur.lastrowid), "code": code, "expires_at": expires.strftime("%Y-%m-%d %H:%M")}


def get_reset_request(email: str, code: str) -> dict[str, Any] | None:
    email = email.strip().lower()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT rr.id, rr.user_id, rr.code_hash, rr.expires_at
            FROM reset_requests rr
            JOIN users u ON u.id = rr.user_id
            WHERE u.email=? AND rr.used=0
            ORDER BY rr.id DESC LIMIT 1
            """,
            (email,),
        ).fetchone()
    if not row:
        return None
    try:
        expires = datetime.fromisoformat(row["expires_at"])
    except ValueError:
        return None
    if expires < _now():
        return None
    if not secrets.compare_digest(_hash_code(code), row["code_hash"]):
        return None
    return {"id": row["id"], "user_id": row["user_id"]}


def mark_reset_used(reset_id: int) -> None:
    with _connect() as conn:
        conn.execute("UPDATE reset_requests SET used=1 WHERE id=?", (reset_id,))