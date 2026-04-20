
from fastapi import FastAPI
from Wroutes import router as wicket_router


app = FastAPI(
    title="Match Scoreboard API",)

app.include_router(wicket_router,     prefix="/api/v1", tags=["Wickets"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}