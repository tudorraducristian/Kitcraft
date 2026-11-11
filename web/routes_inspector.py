"""Paginile inspectorului. Se umplu în faza 3."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from web import app as web_app

router = APIRouter(prefix="/inspector")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return web_app.TEMPLATES.TemplateResponse(request, "inspector/index.html", {})
