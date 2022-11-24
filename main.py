from fastapi import FastAPI
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import Dict, List, Sequence

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.filedb.filestore import RamStorage
from whoosh.analysis import StemmingAnalyzer

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

class SearchEngine:

    def __init__(self, schema):
        self.schema = schema
        schema.add('raw', TEXT(stored=True))
        self.ix = RamStorage().create_index(self.schema)

    def index_documents(self, docs: Sequence):
        writer = self.ix.writer()
        for doc in docs:
            d = {k: v for k,v in doc.items() if k in self.schema.stored_names()}
            d['raw'] = json.dumps(doc) # raw version of all of doc
            writer.add_document(**d)
        writer.commit(optimize=True)

    def get_index_size(self) -> int:
        return self.ix.doc_count_all()

    def query(self, q: str, fields: Sequence, highlight: bool=True) -> List[Dict]:
        search_results = []
        with self.ix.searcher() as searcher:
            results = searcher.search(MultifieldParser(fields, schema=self.schema).parse(q))
            for r in results:
                d = json.loads(r['raw'])
                if highlight:
                    for f in fields:
                        if r[f] and isinstance(r[f], str):
                            d[f] = r.highlights(f) or r[f]

                search_results.append(d)

        return search_results


docs = [
    {
        "id": "1",
        "title": "First document banana",
        "description": "This is the first document we've added in San Francisco!",
        "tags": ['foo', 'bar'],
        "extra": "kittens and cats"
    },
    {
        "id": "2",
        "title": "Second document hatstand",
        "description": "The second one is even more interesting!",
        "tags": ['alice'],
        "extra": "foals and horses"
    },
    {
        "id": "3",
        "title": "Third document slug",
        "description": "The third one is less interesting!",
        "tags": ['bob'],
        "extra": "bunny and rabbit"
    },
]

schema = Schema(
    id=ID(stored=True),
    title=TEXT(stored=True),
    description=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    tags=KEYWORD(stored=True)
)

engine = SearchEngine(schema)
engine.index_documents(docs)

# print(f"indexed {engine.get_index_size()} documents")

fields_to_search = ["title", "description", "tags"]

@api_router.get("/search/", status_code=200)
def search(q: Optional[str] = None):
    if not q:
        return "fail"
    result = engine.query(q, fields_to_search, highlight=True)
    return {results: result}