from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from app.config import settings


def load_xray_config() -> dict[str, Any]:
    path = Path(settings.xray_config_path)
    if not path.exists():
        raise FileNotFoundError(f"Xray config not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_xray_config(data: dict[str, Any]) -> None:
    path = Path(settings.xray_config_path)
    backup_path = path.with_suffix(".json.bak")
    if path.exists():
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def restart_xray() -> None:
    result = subprocess.run(
        ["/bin/systemctl", "restart", settings.xray_service_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to restart xray: stdout={result.stdout!r} stderr={result.stderr!r}"
        )


def get_clients_node(data: dict[str, Any]) -> list[dict[str, Any]]:
    inbounds = data.get("inbounds", [])
    if not inbounds:
        raise ValueError("No inbounds found in Xray config")
    settings_node = inbounds[0].get("settings", {})
    clients = settings_node.get("clients")
    if clients is None:
        raise ValueError("No clients section found in Xray config")
    return clients


def sync_client(uuid_value: str, email: str, is_active: bool) -> None:
    data = load_xray_config()
    clients = get_clients_node(data)
    existing = next((c for c in clients if c.get("id") == uuid_value), None)

    if is_active:
        if existing is None:
            clients.append({"id": uuid_value, "flow": "xtls-rprx-vision", "email": email})
        else:
            existing["flow"] = "xtls-rprx-vision"
            existing["email"] = email
    else:
        if existing is not None:
            clients.remove(existing)

    save_xray_config(data)
    restart_xray()


def remove_client(uuid_value: str) -> None:
    data = load_xray_config()
    clients = get_clients_node(data)
    existing = next((c for c in clients if c.get("id") == uuid_value), None)
    if existing is not None:
        clients.remove(existing)
        save_xray_config(data)
        restart_xray()


def build_vless_link(uuid_value: str, name: str) -> str:
    safe_name = "".join(ch for ch in name if ch.isascii() and (ch.isalnum() or ch in "-_")) or "VPN"
    return (
        f"vless://{uuid_value}@{settings.server_ip}:{settings.server_port}"
        f"?encryption=none"
        f"&security=reality"
        f"&sni={settings.sni}"
        f"&fp=chrome"
        f"&pbk={settings.public_key}"
        f"&sid={settings.short_id}"
        f"&type=tcp"
        f"&flow=xtls-rprx-vision"
        f"#{safe_name}"
    )
