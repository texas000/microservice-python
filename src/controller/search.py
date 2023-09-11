from fastapi import APIRouter, Request
from urllib.parse import unquote
from googletrans import Translator
import requests
from bs4 import BeautifulSoup

from module import db
router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/recommendation")
async def recommendation(query: str):
    translator = Translator()
    language = translator.detect(query).lang
    url = f"https://clients1.google.com/complete/search?client=firefox&q={query}&hl={language}"
    response = requests.get(url)
    suggestions = response.json()[1]
    return({"data": suggestions})

@router.get("/naver")
async def naver_search(search_query: str):
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
    return res