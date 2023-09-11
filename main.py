from fastapi import FastAPI, APIRouter
import json
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
from src import register

description = """
# 🚀 Microservice
"""

app = FastAPI(
    title="New York Select Shop",
    description=description,
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)

router = APIRouter()
register.include_routers(router)

origins = [
    "https://newyorkselectshop.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')