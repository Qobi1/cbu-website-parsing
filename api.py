from flask import Flask
from flask_restx import Api, Resource
from sqlalchemy.orm import scoped_session
from sqlalchemy import desc
from models import SessionLocal, NewsItem

app = Flask(__name__)

api = Api(app, title="CBU News API", version="1.0", description="News API with Swagger")

db_session = scoped_session(SessionLocal)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


ns = api.namespace('news', description='News operations')


@ns.route('/')
class NewsList(Resource):
    def get(self):
        """Return all unique news items"""
        db = db_session()

        news_list = db.query(NewsItem).order_by(desc(NewsItem.id)).all()

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
