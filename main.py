from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
import json
from pymongo import MongoClient, DESCENDING
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
import requests
from httpx import AsyncClient
from bs4 import BeautifulSoup
from urllib.parse import unquote
from googletrans import Translator
from datetime import datetime
from markdown import markdown
from ftplib import FTP
from io import BytesIO
import psycopg2
import openai
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

origins = [
    "https://smartjinny.com",
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

###### Connect Database

db = get_database()
mongo = db["SMARTJIN"]

@app.get("/health", tags=["health"], summary="Health check API")
async def root():
    # Main page redirect to the Swagger Doc
    return {"data": "true"}

@app.get("/")
async def root():
    # Main page redirect to the Swagger Doc
    return RedirectResponse("/docs")

@app.get("/search", tags=["search"])
async def naver_search(search_query: str, request: Request):
    query = unquote(search_query)
    translator = Translator()
    lan = translator.detect(query)

    url = f"https://search.naver.com/search.naver?query={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    result_list = []
    # NAVER BOX
    for li in soup.find_all("li", class_="bx"):
        # Define a list of possible class names for the title element
        title_classes=["news_tit", "link_tit", "info_title", "api_txt_lines"]

        # Find the title element using any of the possible class names
        title = None
        for class_name in title_classes:
            title = li.find('a', class_=class_name)
            if title:
                break
        if title is None:
            continue
        link = title["href"]
        
        description_classes=["api_txt_lines dsc_txt", "api_txt_lines dsc_txt_wrap"]
        
        description = None
        for class_name in description_classes:
            isDescription = li.find('a', class_=class_name)
            if isDescription:
                description = li.find('a', class_=class_name).get_text()
                break
        if title is None:
            continue
        # description = li.find("div", class_="api_txt_lines dsc_txt").get_text()
        result_list.append({"title": title.get_text(), "link": link, "description": description})
    res = {"total": len(result_list), "engine": "naver", "data": result_list, "query": query, "lan": lan.lang}
    search_history = mongo["search_history"]
    now = datetime.now()
    result = search_history.insert_one({"request":request.headers, "res": res, "created": now})
    print({"log_name": "search_history", "id": str(result.inserted_id)})
    return res

@app.get("/search/recommendation", tags=["search"])
async def recommendation(query: str):
    translator = Translator()
    language = translator.detect(query).lang
    url = f"https://clients1.google.com/complete/search?client=firefox&q={query}&hl={language}"
    response = requests.get(url)
    suggestions = response.json()[1]
    return({"data": suggestions})

@app.get("/search/history", tags=["search"])
async def getHistory():
    coll = mongo["search_history"]
    return_string=[]
    his = coll.find({}, {'_id': 0, 'request': 0}).sort( "created", DESCENDING ).limit(20)
    for x in his:
        # print(x)
        result = json.dumps(x, default=str)
        sanitized = json.loads(result)
        return_string.append(sanitized)
    return JSONResponse(content=return_string)

@app.get("/blog/content", tags=["blog"])
async def content(slug: str):
    url = f"https://test-711dbb.webflow.io/blog/{slug}"
    # Send a GET request to the URL
    response = requests.get(url)

    status = response.status_code

    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    head = {}
    title = soup.find("title")
    
    head["title"]=title.get_text()
    head["description"]=soup.find("meta", {"property": "og:description"}).attrs['content']
    head["generator"]="Smartjinny"

    body_content = soup.find("body")

   # Get the HTML representation of the body content
    body_html = body_content.prettify()
    if(status!=200):
        return False
    else:
        return {"data": {"head":head, "body": body_html, "status": status}}

@app.post("/blog/push", tags=["blog"])
async def convert_markdown_to_html(request: Request):
    # Get the markdown text from the request
    body = await request.body()
    parsed_body = json.loads(body)
    
    html_collection = mongo["html_documents"]
    print(parsed_body["markdown"])
    # Convert the markdown text to HTML
    html_text = markdown(parsed_body["markdown"])
    # Save the HTML document to MongoDB
    html_document = {"html": html_text, "created":datetime.now(), "editor": "SMARTJINNY", "updated": datetime.now(), "title": parsed_body["title"], "description": parsed_body["description"], "slug": parsed_body["slug"]}
    result = html_collection.insert_one(html_document)

    # Return the HTML document in the response
    return html_text

@app.get("/blog/list", tags=["blog"])
async def getSocialList():
    col = mongo["html_documents"]
    return_string=[]
    for x in col.find({}, {'html': 0}).limit(100):
        result = json.dumps(x, default=str)
        sanitized = json.loads(result)
        return_string.append(sanitized)
    return JSONResponse(content=return_string)

@app.get("/blog/slug", tags=["blog"])
async def getSocialList(path: str):
    col = mongo["html_documents"]
    content = col.find_one({'slug': path})
    result = json.dumps(content, default=str)
    return json.loads(result)

@app.get("/social/{id}", tags=["data"])
async def getSocial(id: str):
    col1 = mongo["social"]
    social = col1.find_one({'identifier': id}, {'_id': 0})
    result = json.dumps(social, default=str)
    return json.loads(result)

@app.get("/social/", tags=["list"])
async def getSocialList():
    col = mongo["social"]
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

RED_LIST_API_URL = "https://ws-public.interpol.int/notices/v1/red"

@app.get("/redlist", tags=["interpol"])
async def get_red_list():
    response = requests.get(RED_LIST_API_URL)
    data = response.json()
    return {"redlist": data}

@app.get("/redlist/{notice_id}", tags=["interpol"])
async def get_red_notice(notice_id: str):
    notice_url = f"{RED_LIST_API_URL}/{notice_id}"
    response = requests.get(notice_url)
    data = response.json()
    return {"red_notice": data}

openai.api_key=os.environ.get('OPENAI_API_KEY')

@app.get("/ai/code", tags=["ai"])
async def code_gpt(query: str):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=query,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response

FTP_HOST = os.environ.get('FTP_HOST')
FTP_USER = os.environ.get('FTP_USER')
FTP_PASS = os.environ.get('FTP_PASS')
FTP_DIR = '/shares/USB_Storage/smartjinny'

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
        ftp.cwd(FTP_DIR)
        file_name = file.filename
        if file_name in ftp.nlst():
            file_extension = file.filename.split('.')[-1]
            file_base_name = file.filename.split('.')[0]
            i = 1
            while f"{file_base_name}_{i}.{file_extension}" in ftp.nlst():
                i +=1
            file_name = f"{file_base_name}_{i}.{file_extension}" 
        ftp.storbinary(f"STOR {file_name}", file.file)
        upload_col = mongo["file_upload"]
        metadata = {"filename": file_name, "content_type": file.content_type, "updated": datetime.now()}
        upload_col.insert_one(metadata)
    return {"filename": file_name}

# Vercel has timeout of 10 second in free version
@app.get("/download/{filename}")
async def download_file(filename: str):
    buffer = BytesIO()
    with FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
        ftp.cwd(FTP_DIR)
        ftp.retrbinary(f"RETR {filename}", buffer.write)
        ftp.quit()
    buffer.seek(0)
    download_col = mongo["file_download"]
    metadata = {"filename": filename, "updated": datetime.now()}
    download_col.insert_one(metadata)

    return StreamingResponse(buffer, headers={'Content-Disposition': f'inline; filename="{filename}"'})

@app.get("/assets")
async def asset_list():
    col = mongo["file_upload"]
    return_string=[]
    for x in col.find({}, {'content_type': 0}).limit(100):
        result = json.dumps(x, default=str)
        sanitized = json.loads(result)
        return_string.append(sanitized)
    return JSONResponse(content=return_string)

POSTGRE_CONNECT = os.environ.get('POSTGRE_CONNECT')
conn = psycopg2.connect(POSTGRE_CONNECT)

@app.get("/postgresql")
async def test():
    with conn.cursor() as cur:
        # cur.execute("SELECT now()")
        cur.execute("""
        select now();
        """)
        res = cur.fetchall()
        conn.commit()
        return res