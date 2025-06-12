import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
DATABASE_ID = os.environ["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

KEYWORDS = ["맞춤형화장품", "화장품", "뷰티", "맞춤형화장품조제관리사"]

def post_to_notion(title, url, source):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": title}}]},
            "링크": {"url": url},
            "날짜": {"date": {"start": datetime.now().isoformat()}},
            "출처": {"rich_text": [{"text": {"content": source}}]}
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("✅ 등록:", title)
    else:
        print(f"❌ 실패: {title} → {response.status_code} {response.text}")

def contains_keyword(text):
    return any(keyword in text for keyword in KEYWORDS)

def fetch_naver_news():
    print("👉 네이버 뉴스 테스트 수집 중...")
    url = "https://search.naver.com/search.naver?where=news&query=%EB%A7%9E%EC%B6%A4%ED%98%95%ED%99%94%EC%9E%A5%ED%92%88"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".list_news div.news_area")
    print(f"총 {len(items)}개 항목 발견")
    for item in items:
        a_tag = item.select_one("a.news_tit")
        if a_tag:
            title = a_tag["title"]
            link = a_tag["href"]
            print(" -", title)
            if contains_keyword(title):
                post_to_notion(title, link, "네이버뉴스")

# 실행
fetch_naver_news()
