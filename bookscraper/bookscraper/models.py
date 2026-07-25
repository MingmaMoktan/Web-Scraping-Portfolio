from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    title = Column(String(255), nullable=False)
    upc = Column(String(100), nullable=True)
    product_type = Column(String(100), nullable=True)
    price_excl_tax = Column(Float, nullable=True)
    price_incl_tax = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    availability = Column(Integer, nullable=True)  # Changed to Integer to match pipeline output
    num_reviews = Column(Integer, nullable=True)
    stars = Column(Integer, nullable=True)         # Changed to Integer to match pipeline output
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

# Fixed: Pass db_url into the function parameter!
def db_connect(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()