import typer
import uvicorn

from ai_app.config import Stage, get_config


def launch_app(environment: Stage = Stage.local, workers: int = 1):
    uvicorn.run(
        "ai_app.app:build_app",  # String definition is required for reload and multiple workers.
        host="0.0.0.0" if environment == Stage.prod else "localhost",
        port=get_config().port,
        workers=workers,
        reload=environment == Stage.local,
        factory=True,
    )


def main():
    typer.run(launch_app)


if __name__ == "__main__":
    main()
