"""FastAPI entrypoint for BananaKart backend."""
import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from fastapi import FastAPI

from .routes import analyze, simulate

app = FastAPI(title="BananaKart API")

app.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
app.include_router(simulate.router, prefix="/simulate", tags=["simulation"])
