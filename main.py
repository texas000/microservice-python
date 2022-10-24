from fastapi import FastAPI
import json

app = FastAPI()

# Opening JSON file
f = open('social.json', encoding='utf-8')  
# returns JSON object as 
# a dictionary
data = json.load(f)

@app.get("/")
async def root():
    return data

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