from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse

from app.auth import check_auth
from app.services.client_service import (
    create_client_record,
    delete_client_record,
    get_client,
    set_client_active,
)
from app.services.qr_service import build_qr
from app.services.xray_service import build_vless_link, remove_client, sync_client

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(check_auth)],
)


@router.post("/create")
def create_client(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    note: str = Form(""),
):
    client = create_client_record(name=name.strip(), note=note.strip())
    background_tasks.add_task(
        sync_client,
        uuid_value=client["uuid"],
        email=client["name"],
        is_active=True,
    )
    return RedirectResponse(url=f"/clients/{client['id']}", status_code=303)


@router.get("/{client_id}")
def client_detail(client_id: int, request: Request):
    from app.main import templates

    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    link = build_vless_link(client["uuid"], client["name"])
    qr_path = Path(f"data/qrcodes/client_{client_id}.png")
    build_qr(qr_path, link)

    return templates.TemplateResponse(
        request=request,
        name="client_detail.html",
        context={
            "client": client,
            "link": link,
            "qr_url": f"/clients/{client_id}/qr",
            "package_url": f"/clients/{client_id}/package",
        },
    )


@router.get("/{client_id}/qr")
def client_qr(client_id: int):
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    link = build_vless_link(client["uuid"], client["name"])
    qr_path = Path(f"data/qrcodes/client_{client_id}.png")
    build_qr(qr_path, link)
    return FileResponse(qr_path)


@router.get("/{client_id}/package")
def client_package(client_id: int):
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    link = build_vless_link(client["uuid"], client["name"])
    qr_path = Path(f"data/qrcodes/client_{client_id}.png")
    build_qr(qr_path, link)

    readme = f"""Client name: {client['name']}

Important:
This access is intended for 1 device.
If you need a second phone or laptop, create a separate UUID.

How to connect Android:
1. Install v2ray (https://play.google.com/store/apps/details?id=com.v2ray.client)
2. Open the app.
3. Tap "+".
4. Choose "Scan QR code" or "Import from clipboard".
5. Use the QR code or the link from config.txt.

VLESS link:
{link}
"""

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt", readme)
        zf.writestr("config.txt", link)
        if qr_path.exists():
            zf.write(qr_path, arcname="qr.png")

    buffer.seek(0)
    safe_name = f"client_{client_id}_package.zip"
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.post("/{client_id}/toggle")
def toggle_client(background_tasks: BackgroundTasks, client_id: int):
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_state = not bool(client["is_active"])
    set_client_active(client_id, new_state)
    background_tasks.add_task(
        sync_client,
        uuid_value=client["uuid"],
        email=client["name"],
        is_active=new_state,
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/{client_id}/delete")
def delete_client(background_tasks: BackgroundTasks, client_id: int):
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    delete_client_record(client_id)
    background_tasks.add_task(remove_client, client["uuid"])
    return RedirectResponse(url="/", status_code=303)
