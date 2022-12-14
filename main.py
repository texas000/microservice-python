from fastapi import FastAPI
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
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
    # Main page redirect to the Swagger Doc
    return RedirectResponse("https://api.smartjinny.com/docs")

@app.get("/social/{id}", tags=["data"])
async def getSocial(id: str):
    db = get_database()
    col1 = db["SMARTJIN"]["social"]
    print(id)
    social = col1.find_one({'identifier': id}, {'_id': 0})
    result = json.dumps(social, default=str)
    return json.loads(result)

@app.get("/social/", tags=["list"])
async def getSocialList():
    db = get_database()
    col = db["SMARTJIN"]["social"]
    return_string=[]
    for x in col.find({}).limit(100):
        result = json.dumps(x["identifier"], default=str)
        sanitized = json.loads(result)
        return_string.append(sanitized)
    return JSONResponse(content=return_string)

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
