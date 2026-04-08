from __future__ import annotations

import subprocess

from app.db import get_connection
from app.services.client_service import list_clients

XRAY_API_PORT = 10085
XRAYCTL = "/usr/local/bin/xray"


def _run_xray_api_request(pattern: str) -> int:
    cmd = [
        XRAYCTL,
        "api",
        "statsquery",
        f"--server=127.0.0.1:{XRAY_API_PORT}",
        "-pattern",
        pattern,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0

    stdout = result.stdout.strip()
    if not stdout or stdout == "{}":
        return 0

    digits = []
    for token in stdout.replace("\n", " ").split():
        if token.isdigit():
            digits.append(int(token))
    return digits[-1] if digits else 0


def bytes_to_mb(value: int) -> float:
    return round(value / 1024 / 1024, 2)


def get_stats_summary() -> dict:
    version_result = subprocess.run(
        [XRAYCTL, "version"],
        capture_output=True,
        text=True,
    )
    version_line = ""
    if version_result.stdout.strip():
        version_line = version_result.stdout.strip().splitlines()[0]
    elif version_result.stderr.strip():
        version_line = version_result.stderr.strip().splitlines()[0]

    api_check = subprocess.run(
        ["ss", "-ltnp"],
        capture_output=True,
        text=True,
    )
    api_ready = "127.0.0.1:10085" in api_check.stdout or ":10085" in api_check.stdout

    return {
        "stats_enabled": api_ready,
        "message": "Накопительная статистика активна." if api_ready else "API stats не слушает 10085.",
        "xray_version": version_line,
    }


def _accumulate_and_store(client_uuid: str, stat_key: str) -> dict[str, float]:
    up_pattern = f"user>>>{stat_key}>>>traffic>>>uplink"
    down_pattern = f"user>>>{stat_key}>>>traffic>>>downlink"

    current_up = _run_xray_api_request(up_pattern)
    current_down = _run_xray_api_request(down_pattern)

    conn = get_connection()
    row = conn.execute(
        "SELECT raw_up_bytes, raw_down_bytes, traffic_up_mb, traffic_down_mb FROM clients WHERE uuid = ?",
        (client_uuid,),
    ).fetchone()

    prev_raw_up = int(row["raw_up_bytes"]) if row else 0
    prev_raw_down = int(row["raw_down_bytes"]) if row else 0
    total_up_mb = float(row["traffic_up_mb"]) if row else 0.0
    total_down_mb = float(row["traffic_down_mb"]) if row else 0.0

    delta_up = current_up - prev_raw_up if current_up >= prev_raw_up else current_up
    delta_down = current_down - prev_raw_down if current_down >= prev_raw_down else current_down

    total_up_mb = round(total_up_mb + bytes_to_mb(delta_up), 2)
    total_down_mb = round(total_down_mb + bytes_to_mb(delta_down), 2)

    conn.execute(
        '''
        UPDATE clients
        SET raw_up_bytes = ?, raw_down_bytes = ?, traffic_up_mb = ?, traffic_down_mb = ?
        WHERE uuid = ?
        ''',
        (current_up, current_down, total_up_mb, total_down_mb, client_uuid),
    )
    conn.commit()
    conn.close()

    return {
        "up_mb": total_up_mb,
        "down_mb": total_down_mb,
        "total_mb": round(total_up_mb + total_down_mb, 2),
    }


def get_client_traffic_map() -> dict[str, dict[str, float]]:
    traffic_map = {}
    for client in list_clients():
        stat_key = client.get("email") or client["uuid"]
        traffic_map[client["uuid"]] = _accumulate_and_store(client["uuid"], stat_key)
    return traffic_map
