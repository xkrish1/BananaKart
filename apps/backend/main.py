"""FastAPI entrypoint for BananaKart backend."""
import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from .core.env_loader import load_env

load_env()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analyze, health, simulate

app = FastAPI(title="BananaKart API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://green-kart-view.vercel.app",
    "https://bananakart.tech",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["system"])
app.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
app.include_router(simulate.router, prefix="/simulate", tags=["simulation"])
