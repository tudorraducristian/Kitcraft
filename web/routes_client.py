"""Paginile clientului. Se umplu în faza 2."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from web import app as web_app

router = APIRouter(prefix="/client")


@router.get("/cereri", response_class=HTMLResponse)
def cereri(request: Request):
    return web_app.TEMPLATES.TemplateResponse(request, "client/cereri.html", {})
