from .db import engine, Base
from . import models

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating tables...")
    init_db()
    print("Tables created.")
