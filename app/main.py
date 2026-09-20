from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Employee Data Analysis",
    version="0.1.0",
    description="Secure local-first employee CSV analysis application.",
)

app.include_router(router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Employee Data Analysis API is running."}
