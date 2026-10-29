from fastapi import FastAPI
import pyjokes
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

@app.get("/")
async def root():
    random_joke = pyjokes.get_joke("en", "neutral")
    return {"random_joke": random_joke, "version": "v2"}

Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(app)
