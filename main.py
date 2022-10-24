from fastapi import FastAPI
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

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

@app.get("/{id}")
async def gets(id):
    for ga in data["dataset"]:
        if ga["identifier"]==id:
            return ga        
    return "fail"    

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

f.close()

