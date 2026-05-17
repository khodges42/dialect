"""FastAPI application entrypoint."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Dialect", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("bbs.server.app:app", host="127.0.0.1", port=8000, reload=True)
