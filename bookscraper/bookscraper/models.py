from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    upc = Column(String(100), nullable=True)
    product_type = Column(String(100), nullable=True)
    price_excl_tax = Column(Float, nullable=True)
    price_incl_tax = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    availability = Column(String(100), nullable=True)
    num_reviews = Column(Integer, nullable=True)
    stars = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    

# Database connection setup
def db_connect():
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
    