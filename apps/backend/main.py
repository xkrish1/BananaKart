"""FastAPI entrypoint for BananaKart backend."""
from fastapi import FastAPI

from routes import analyze, simulate

app = FastAPI(title="BananaKart API")

app.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
app.include_router(simulate.router, prefix="/simulate", tags=["simulation"])
