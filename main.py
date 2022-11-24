from fastapi import FastAPI
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

description = """
Microservice for Smartjinny🚀

## Hello

You can make wonderful things
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
            "url": "https://smartjinny.com/",
        },
    },
]

app = FastAPI(
    title="Smartjinny Microservice",
    description=description,
    version="0.0.1",
    terms_of_service="https://smartjinny.com/terms/",
    contact={
        "name": "Smartjinny Microservice",
        "url": "https://smartjinny.com/contact/",
        "email": "admin@smartjinny.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
)

# Connect Database
def get_database():

    CONNECTION_STRING = os.environ.get('MONGODB_URI')
    # Create a connection using MongoClient
    client = MongoClient(CONNECTION_STRING)
    return client

# Opening JSON file
f = open('social.json', encoding='utf-8')  
# returns JSON object as 
# a dictionary
data = json.load(f)

@app.get("/")
async def root():
    db = get_database()
    col = db["SMARTJIN"]["agent"]
    return col.find_one({},{'_id': 0})

@app.get("/sales/{store}", tags=["data"])
async def getSales(store: str):
    db = get_database()
    col = db["sample_supplies"]["sales"]
    #sample 5bd761dcae323e45a93ccfeb
    return col.find({'storeLocation': store}, {'_id': 0})

@app.get("/sales/", tags=["list"])
async def getSales():
    db = get_database()
    col = db["sample_supplies"]["sales"]
    return col.find({},{'_id': 0,}).limit(50)

@app.get("/data/{id}", tags=["data"])
async def gets(id):
    for ga in data["dataset"]:
        if ga["identifier"]==id:
            return ga        
    return "fail"    

@app.get("/data/", tags=["list"])
async def list_item():
    new_list = []
    for ga in data["dataset"]:
        new_list.append(ga["identifier"])
    return {"list": new_list}

f.close()