from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.db import get_connection


def list_clients() -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        '''
        SELECT id, name, uuid, email, is_active, created_at, note,
               traffic_up_mb, traffic_down_mb, raw_up_bytes, raw_down_bytes
        FROM clients
        ORDER BY id DESC
        '''
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_client_record(name: str, note: str = "") -> dict[str, Any]:
    client_uuid = str(uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO clients (name, uuid, email, is_active, created_at, note, traffic_up_mb, traffic_down_mb, raw_up_bytes, raw_down_bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (name, client_uuid, name, 1, created_at, note, 0.0, 0.0, 0, 0),
    )
    client_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": client_id,
        "name": name,
        "uuid": client_uuid,
        "email": name,
        "is_active": True,
        "created_at": created_at,
        "note": note,
        "traffic_up_mb": 0.0,
        "traffic_down_mb": 0.0,
        "raw_up_bytes": 0,
        "raw_down_bytes": 0,
    }


def get_client(client_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute(
        '''
        SELECT id, name, uuid, email, is_active, created_at, note,
               traffic_up_mb, traffic_down_mb, raw_up_bytes, raw_down_bytes
        FROM clients
        WHERE id = ?
        ''',
        (client_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def set_client_active(client_id: int, is_active: bool) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE clients SET is_active = ? WHERE id = ?",
        (1 if is_active else 0, client_id),
    )
    conn.commit()
    conn.close()


def delete_client_record(client_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
