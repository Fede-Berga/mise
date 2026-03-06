from fastapi import Depends, FastAPI

from common.app.auth import get_current_user

from .api.controllers.menu_gen_controller import router as menu_gen_router


def create_app() -> FastAPI:
    app = FastAPI(title="Mise AI Service", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"status": "ok", "service": "ai-service"}

    app.include_router(
        menu_gen_router,
        prefix="/ai",
        tags=["ai"],
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
