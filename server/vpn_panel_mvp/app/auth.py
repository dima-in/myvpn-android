from fastapi import HTTPException, Request, status

from app.config import settings

SESSION_COOKIE = "vpn_panel_session"


def check_auth(request: Request) -> None:
    session_value = request.cookies.get(SESSION_COOKIE)
    if session_value != settings.app_secret:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Authentication required",
            headers={"Location": "/login"},
        )
