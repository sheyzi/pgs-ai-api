import os
from fastapi import FastAPI
from fastapi_extras.errors import configure_error_handlers
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


if "GOOGLE_API_KEY" not in os.environ:
    raise Exception("GOOGLE_API_KEY not provided in the env")


def configure_cors(app: FastAPI):
    origin_env = os.environ.get("CORS_ORIGINS")

    origins = []

    if not origin_env:
        origins = ["http://localhost:5173"]

    origins = origin_env.split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_router(app: FastAPI):
    from api.router import router

    app.include_router(router=router)


def create_app() -> FastAPI:
    app = FastAPI()
    configure_router(app)
    configure_cors(app)
    configure_error_handlers(app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)
