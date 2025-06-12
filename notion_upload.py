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

def post_to_notion(title, url):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": title}}]},
            "링크": {"url": url},
            "날짜": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("✅ 등록:", title)
    else:
        print(f"❌ 실패: {title} → {response.status_code} {response.text}")

def contains_keyword(text):
    return any(keyword in text for keyword in KEYWORDS)

def fetch_mfds():
    res = requests.get("https://www.mfds.go.kr/brd/m_99/list.do")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".board_list tbody tr")
    for row in rows:
        title = row.select_one("td.subject a").text.strip()
        link = "https://www.mfds.go.kr" + row.select_one("td.subject a")["href"]
        if contains_keyword(title):
            post_to_notion(title, link)

def fetch_nedrug():
    try:
        res = requests.post(
            "https://nedrug.mfds.go.kr/pbp/CCBBB01/getList.do",
            data={"page": "1", "pageUnit": "10"},
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (compatible; notion-bot/1.0)"
            },
            timeout=10
        )
        data = res.json()
        items = data.get("data", [])
        for item in items:
            title = item["bbsTitl"]
            link = f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getView.do?bbsSn={item['bbsSn']}"
            if contains_keyword(title):
                post_to_notion(title, link)
    except Exception as e:
        print("❌ 의약품안전나라 응답 파싱 실패:", e)

def fetch_kcia():
    res = requests.get("https://www.kcia.or.kr/notice/notice_list.asp")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".board_list tbody tr")
    for row in rows:
        link_tag = row.select_one("td.subject a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://www.kcia.or.kr/notice/" + link_tag["href"]
            if contains_keyword(title):
                post_to_notion(title, link)

def fetch_korcham():
    res = requests.get("https://www.korcham.net/nCham/Service/Economy/appl/KCCI_notice_list.asp")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".tbl_list tbody tr")
    for row in rows:
        link_tag = row.select_one("td.subject a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://www.korcham.net" + link_tag["href"]
            if contains_keyword(title):
                post_to_notion(title, link)

# 실행
fetch_mfds()
fetch_nedrug()
fetch_kcia()
fetch_korcham()
