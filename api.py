from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import SessionLocal, NewsItem

app = FastAPI(title="CBU News API")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/news")
def get_news(db: Session = Depends(get_db)):
    # Get all news items ordered by published_date descending
    news_list = db.query(NewsItem).order_by(desc(NewsItem.published_date)).all()

    seen_links = set()
    unique_news = []
    for item in news_list:
        if item.link not in seen_links:
            seen_links.add(item.link)
            unique_news.append({
                "id": item.id,
                "title": item.title,
                "link": item.link,
                "image": item.image,
                "published_date": item.published_date,
                "last_modified": item.last_modified,
                "content": item.content
            })

    return {"news": unique_news}
