from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.auth import SESSION_COOKIE, check_auth
from app.db import init_db
from app.routers.clients import router as clients_router
from app.services.client_service import list_clients
from app.services.system_service import get_system_metrics, get_xray_status
from app.services.xray_service import build_vless_link
from app.services.xray_stats_service import get_client_traffic_map, get_stats_summary
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="VPN Panel MVP+")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(clients_router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    has_error = request.query_params.get("error") == "1"
    error_block = (
        '<p style="color:#dc2626;margin:0 0 12px">Неверный пароль</p>' if has_error else ""
    )
    return f"""
    <html><body style="font-family:sans-serif;max-width:400px;margin:100px auto">
    <h2>VPN Panel | Вход</h2>
    {error_block}
    <form method="post" action="/login">
        <input type="password" name="password" placeholder="Пароль"
               style="width:100%;padding:8px;margin-bottom:10px;box-sizing:border-box">
        <button type="submit" style="width:100%;padding:8px;background:#2563eb;color:white;border:none;cursor:pointer">
            Войти
        </button>
    </form>
    </body></html>
    """


@app.post("/login")
def login(password: str = Form(...)):
    if password != settings.app_secret:
        return RedirectResponse(url="/login?error=1", status_code=303)

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=settings.app_secret,
        httponly=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/")
def index(request: Request, _: None = Depends(check_auth)):
    clients = list_clients()
    traffic_map = get_client_traffic_map()

    for client in clients:
        client["link"] = build_vless_link(client["uuid"], client["name"])
        client["is_active"] = bool(client["is_active"])
        tm = traffic_map.get(client["uuid"], {})
        client["traffic_up_mb"] = tm.get("up_mb", 0.0)
        client["traffic_down_mb"] = tm.get("down_mb", 0.0)
        client["traffic_total_mb"] = tm.get("total_mb", 0.0)

    metrics = get_system_metrics()
    xray_status = get_xray_status()
    stats_summary = get_stats_summary()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "clients": clients,
            "metrics": metrics,
            "xray_status": xray_status,
            "stats_summary": stats_summary,
        },
    )
