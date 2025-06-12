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

def fetch_mfds():
    print("👉 식약처 뉴스 수집 중...")
    res = requests.get("https://www.mfds.go.kr/brd/m_99/list.do")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".board_list tbody tr")
    print(f"총 {len(rows)}개 항목 발견")
    for row in rows:
        title = row.select_one("td.subject a").text.strip()
        link = "https://www.mfds.go.kr" + row.select_one("td.subject a")["href"]
        print(" -", title)
        if contains_keyword(title):
            post_to_notion(title, link, "식약처")

def fetch_nedrug_html():
    try:
        url = "https://nedrug.mfds.go.kr/pbp/CCBBB01/list.do"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code != 200:
            print("❌ 의약품안전나라 응답 실패:", res.status_code)
            return

        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.board_list tbody tr")
        print(f"👉 의약품안전나라에서 {len(rows)}개 항목 수집")
        for row in rows:
            title_tag = row.select_one("td.subject a")
            if title_tag:
                title = title_tag.text.strip()
                link = "https://nedrug.mfds.go.kr" + title_tag.get("href")
                print(" -", title)
                if contains_keyword(title):
                    post_to_notion(title, link, "의약품안전나라")
    except Exception as e:
        print("❌ 의약품안전나라 요청 실패:", e)

def fetch_kcia_news():
    print("👉 대한화장품협회 뉴스 수집 중...")
    res = requests.get("https://kcia.or.kr/home/notice/notice.php")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".board_list tbody tr")
    print(f"총 {len(rows)}개 항목 발견")
    for row in rows:
        link_tag = row.select_one("td.subject a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://kcia.or.kr" + link_tag["href"]
            print(" -", title)
            if contains_keyword(title):
                post_to_notion(title, link, "대한화장품협회-공지")

def fetch_kcia_laws():
    print("👉 대한화장품협회 법 수집 중...")
    res = requests.get("https://kcia.or.kr/home/law/law_01.php")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".board_list tbody tr")
    print(f"총 {len(rows)}개 항목 발견")
    for row in rows:
        link_tag = row.select_one("td.subject a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://kcia.or.kr" + link_tag["href"]
            print(" -", title)
            if contains_keyword(title):
                post_to_notion(title, link, "대한화장품협회-법령")

def fetch_korcham():
    print("👉 대한상공회의소 뉴스 수집 중...")
    res = requests.get("https://www.korcham.net/nCham/Service/Board/appl/notice_list.asp")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".tbl_list tbody tr")
    print(f"총 {len(rows)}개 항목 발견")
    for row in rows:
        link_tag = row.select_one("td.subject a")
        if link_tag:
            title = link_tag.text.strip()
            link = "https://www.korcham.net" + link_tag["href"]
            print(" -", title)
            if contains_keyword(title):
                post_to_notion(title, link, "대한상공회의소")

# 실행
fetch_mfds()
fetch_nedrug_html()
fetch_kcia_news()
fetch_kcia_laws()
fetch_korcham()
