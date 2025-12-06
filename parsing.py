import time
import requests
import schedule
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from models import SessionLocal, NewsItem

# Constants
BASE_URL = "https://cbu.uz"
TASHKENT_TZ = pytz.timezone("Asia/Tashkent")
START_DATE = "01.09.2025"


def get_today_date():
    """Return today's date in dd.mm.yyyy format (Tashkent time)."""
    return datetime.now(TASHKENT_TZ).strftime("%d.%m.%Y")


def parse_news_list():
    end_date = get_today_date()
    news_page_url = f"{BASE_URL}/uz/press_center/news/?DATE_FROM={START_DATE}&DATE_TO={end_date}"
    response = requests.get(news_page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    news_items = soup.find_all("div", class_="grid_item news_item")

    news_data = []
    for item in news_items:
        a_tag = item.find("a", class_="news")
        if not a_tag:
            continue

        title = a_tag.find("div", class_="news__title").get_text(strip=True)
        date_span = a_tag.find("div", class_="news__date").find("span")
        date = date_span.get_text(strip=True) if date_span else None
        link = BASE_URL + a_tag['href']
        image_tag = a_tag.find("div", class_="news__image")
        image_url = BASE_URL + image_tag.find("img")['src'] if image_tag and image_tag.find("img") else None

        # Parse details page for full content
        detail = parse_news_details(link)

        news_data.append({
            "list_title": title,
            "list_date": date,
            "link": link,
            "image": image_url,
            **detail
        })

    return news_data


def parse_news_details(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    h1 = soup.find("h1", class_="heading_border")
    title = h1.get_text(strip=True) if h1 else None

    published_date = None
    date_div = soup.find("div", class_="main_date")
    if date_div:
        sp = date_div.find("span")
        if sp:
            published_date = sp.get_text(strip=True)

    lastmod = None
    lm_div = soup.find("div", class_="lastmodify-page")
    if lm_div:
        lm_span = lm_div.find("span", class_="item-date")
        if lm_span:
            lastmod = lm_span.get_text(strip=True)

    body = None
    body_div = soup.find("div", class_="main_text", itemprop="articleBody")
    if body_div:
        body = body_div.get_text(separator="\n", strip=True)

    return {
        "detail_title": title,
        "published_date": published_date,
        "last_modified": lastmod,
        "body": body
    }


def run_cbu_parser():
    """Run the parser and save news to the database."""
    news_data = parse_news_list()
    if not news_data:
        print("No news found.")
        return

    db = SessionLocal()
    saved_count = 0
    try:
        for item in news_data:
            # Check if this news already exists by link
            exists = db.query(NewsItem).filter(NewsItem.link == item['link']).first()
            if exists:
                continue

            news_item = NewsItem(
                title=item['detail_title'] or item['list_title'],
                link=item['link'],
                image=item['image'],
                published_date=item['published_date'],
                last_modified=item['last_modified'],
                content=item['body']
            )
            db.add(news_item)
            saved_count += 1

        db.commit()
        print(f"Saved {saved_count} new news items to the database.")
    except Exception as e:
        db.rollback()
        print(f"Error saving to DB: {e}")
    finally:
        db.close()


def job():
    now = datetime.now(TASHKENT_TZ)
    print(f"Checking schedule at {now.strftime('%Y-%m-%d %H:%M:%S')} Tashkent time")
    run_cbu_parser()


if __name__ == "__main__":
    # Schedule the parser to run every day at 10:00 Tashkent time
    schedule.every().day.at("14:44").do(job)

    print("Scheduler started. Waiting for 10:00 Tashkent time...")

    # Blocking loop (no threads)
    while True:
        schedule.run_pending()
        time.sleep(30)  # check every 30 seconds