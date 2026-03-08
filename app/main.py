from fastapi import FastAPI
from app.routers import query

app = FastAPI()

app.include_router(query.router)