from fastapi import FastAPI

app = FastAPI(title="TaskHub")


@app.get("/healthz")
async def liveness():
    return {"status": "ok"}
