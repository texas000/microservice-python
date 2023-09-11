from fastapi import FastAPI, APIRouter
import json
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
from src import register

description = """
# 🚀 Microservice
"""

tags_metadata = [
    {
        "name": "data",
        "description": "Get data by id, static json data in env",
    },
    {
        "name": "list",
        "description": "return all the id, static json data in env",
        "externalDocs": {
            "description": "external docs",
            "url": "https://newyorkselectshop.com/",
        },
    },
]

app = FastAPI(
    title="New York Select Shop",
    description=description,
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
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

@app.get("/")
async def root():
    return RedirectResponse("/docs")


