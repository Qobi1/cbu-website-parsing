# CBU News Parser & API

This project parses news from the Central Bank of Uzbekistan (CBU) website and serves it via a FastAPI API.

---

## Requirements

First, install dependencies:

```bash
pip install -r requirements.txt
```

---

## Project Structure

- `parsing.py` — Script for parsing CBU news and saving it to the database.  
- `api.py` — FastAPI server to serve the news data via API.  
- `models.py` — SQLAlchemy models and database setup.

> **Note:** The parser does not save duplicate news. Before adding a news item, it checks if a news item with the same link already exists in the database.

---

## Running the project

Open two separate terminals:

1. **Terminal 1** — Run the parser (parses news daily at 10:00 Tashkent time):

```bash
python parsing.py
```

2. **Terminal 2** — Run the FastAPI server:

```bash
uvicorn api:app --reload
```

---

## API

Once the server is running, you can access the API at:

```
http://127.0.0.1:8000/news
```

This endpoint returns all news stored in the database in JSON format.

---

## Notes

- The parser uses Tashkent timezone for scheduling.  
- News duplication is prevented by checking the `link` field in the database.  
- Make sure the database file (`news.db`) is writable and accessible.

