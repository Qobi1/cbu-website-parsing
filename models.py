from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False, unique=True)
    image = Column(String(1000), nullable=True)
    published_date = Column(String(50), nullable=True)
    last_modified = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)

    def __repr__(self):
        return f"<NewsItem(title={self.title}, published_date={self.published_date})>"


DATABASE_URL = "sqlite:///./news.db"  # change to your DB

# Engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


