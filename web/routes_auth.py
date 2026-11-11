"""Login, înregistrare și logout."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web import app as web_app
from web import auth

router = APIRouter()


def _form_page(request: Request, template: str, *, error: str | None = None,
               values: dict | None = None, status_code: int = 200):
    return web_app.TEMPLATES.TemplateResponse(
        request, template,
        {"error": error, "values": values or {}, "min_password": auth.MIN_PASSWORD},
        status_code=status_code,
    )


def _logged_in(user: auth.User, conn) -> RedirectResponse:
    token = auth.create_session(conn, user.id)
    response = RedirectResponse(auth.home_for(user.role), status_code=303)
    response.set_cookie(
        auth.SESSION_COOKIE, token,
        max_age=auth.SESSION_DAYS * 86400, path="/", httponly=True, samesite="lax",
    )
    return response


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return _form_page(request, "login.html")


@router.post("/login")
def login(request: Request, email: str = Form(""), password: str = Form("")):
    with web_app.get_conn() as conn:
        user = auth.authenticate(conn, email, password)
        if user is None:
            return _form_page(request, "login.html", error="Email sau parolă greșită.",
                              values={"email": email}, status_code=401)
        return _logged_in(user, conn)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return _form_page(request, "register.html")


@router.post("/register")
def register(request: Request, email: str = Form(""), password: str = Form(""),
             brand_name: str = Form("")):
    # Doar aceste trei câmpuri se citesc. Rolul e mereu `client`.
    values = {"email": email, "brand_name": brand_name}
    brand = brand_name.strip()
    if not brand:
        return _form_page(request, "register.html", error="Scrie numele brandului.",
                          values=values, status_code=422)
    with web_app.get_conn() as conn:
        try:
            user = auth.create_user(conn, email, password, "client", brand)
        except auth.EmailTaken:
            return _form_page(request, "register.html", error="Adresa e deja folosită.",
                              values=values, status_code=409)
        except ValueError as exc:
            return _form_page(request, "register.html", error=str(exc),
                              values=values, status_code=422)
        return _logged_in(user, conn)


@router.post("/logout")
def logout(request: Request):
    with web_app.get_conn() as conn:
        auth.delete_session(conn, request.cookies.get(auth.SESSION_COOKIE))
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(auth.SESSION_COOKIE, path="/")
    return response
