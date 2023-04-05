from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, player, search

app = FastAPI()

origins = ["http://localhost", "http://localhost:4200"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(search.router)
app.include_router(player.router)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to Not-ify API!"}
