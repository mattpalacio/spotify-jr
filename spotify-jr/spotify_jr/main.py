from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .routers import auth, player, search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="!not-very-secret")

app.include_router(auth.router)
app.include_router(search.router)
app.include_router(player.router)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to Not-ify API!"}
