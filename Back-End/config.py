
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL-Verbindungs-URL aus deinem Screenshot
SQLALCHEMY_DATABASE_URL = "postgresql://avnadmin:AVNS_wvY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/defaultdb?sslmode=require"

# Engine erstellen
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"sslmode": "require"}
)

# Session erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis für Modelle
Base = declarative_base()

# Datenbank-Session-Handler
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
