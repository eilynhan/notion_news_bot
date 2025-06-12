import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# 환경변수에서 Notion API 키 및 DB ID 읽기
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
DATABASE_ID = os.environ["DATABASE_ID"]

# Notion API 요청 헤더
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 키워드 설정
KEYWORDS = ["맞춤형화장품", "화장품", "뷰티", "맞춤형화장품조제관리사"]

# Notion 페이지 생성 함수
def post_to_notion(title, url, source, date):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": title}}]},
            "링크": {"url": url},
            "날짜": {"date": {"start": date}},
            "출처": {"rich_text": [{"text": {"content": source}}]}
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("✅ 등록:", title)
    else:
        print(f"❌ 실패: {title} → {response.status_code} {response.text}")

# 키워드 포함 여부 확인
def contains_keyword(text):
    return any(keyword in text for keyword in KEYWORDS)

# 네이버 뉴스 크롤링 함수
def fetch_naver_news():
    print("👉 네이버 뉴스 테스트 수집 중...")
    url = "https://search.naver.com/search.naver?where=news&query=%EB%A7%9E%EC%B6%A4%ED%98%95%ED%99%94%EC%9E%A5%ED%92%88"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("ul.list_news > li.bx")
    print(f"총 {len(items)}개 항목 발견")
    for item in items:
        a_tag = item.select_one("a.news_tit")
        press_tag = item.select_one("a.info.press")
        date_tag = item.select("span.info")

        if a_tag and press_tag:
            title = a_tag.get("title") or a_tag.text.strip()
            link = a_tag.get("href")
            press = press_tag.get_text(strip=True).replace("언론사 선택", "")
            date_text = ""
            for tag in date_tag:
                text = tag.get_text(strip=True)
                if '전' in text or '.' in text:
                    date_text = text
                    break
            date_obj = datetime.now().isoformat()  # 날짜 파싱 실패 시 현재 시각으로 대체
            print(" -", title)
            if contains_keyword(title):
                post_to_notion(title, link, press, date_obj)

# 실행
fetch_naver_news()
