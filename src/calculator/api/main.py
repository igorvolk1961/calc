"""Точка входа FastAPI-приложения.

Запуск: ``uvicorn calculator.api.main:app --reload``
"""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from calculator import __version__
from calculator.api.routes import router

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
MAX_BODY_SIZE = 10_000


class MaxBodySizeMiddleware:
    """Отклоняет HTTP-запросы с телом больше ``max_size`` байт."""

    def __init__(self, app, max_size: int = MAX_BODY_SIZE) -> None:
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            content_length = headers.get(b"content-length")
            if content_length is not None:
                try:
                    too_large = int(content_length) > self.max_size
                except ValueError:
                    await _send_error(send, "некорректный Content-Length", 400)
                    return
                if too_large:
                    await _send_error(send, "тело запроса слишком большое", 413)
                    return
        await self.app(scope, receive, send)


async def _send_error(send, detail: str, status: int) -> None:
    body = json.dumps({"detail": detail}).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


app = FastAPI(title="Calculator", version=__version__)
app.add_middleware(MaxBodySizeMiddleware, max_size=MAX_BODY_SIZE)
app.include_router(router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Отдать главную страницу калькулятора."""
    return FileResponse(STATIC_DIR / "index.html")
