from fastapi import FastAPI

from bbs.server.app import create_app


def test_create_app_returns_fastapi_app() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)
