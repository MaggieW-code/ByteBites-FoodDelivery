from fastapi import FastAPI


app = FastAPI(title="Food Delivery API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

