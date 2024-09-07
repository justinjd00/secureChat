import psycopg2
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import sys
from sqlalchemy import text
# Deine Datenbank-URL
SQLALCHEMY_DATABASE_URL = "postgresql://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require"

# Engine erstellen
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def print_system_info():
    """ Gibt die Version von Python, SQLAlchemy und psycopg2 aus """
    print("Python Version:", sys.version)
    try:
        import sqlalchemy
        import psycopg2
        print("SQLAlchemy Version:", sqlalchemy.__version__)
        print("psycopg2 Version:", psycopg2.__version__)
    except ImportError as e:
        print("Fehlende Bibliothek:", e)

def test_connection_with_psycopg2():
    """ Testet die Verbindung mit psycopg2 und gibt die PostgreSQL-Version aus """
    try:
        conn = psycopg2.connect(SQLALCHEMY_DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print("PostgreSQL Version (via psycopg2):", db_version)
        conn.close()
    except Exception as e:
        print("Fehler bei der Verbindung mit psycopg2:", e)

def test_connection_with_sqlalchemy():
    """ Testet die Verbindung mit SQLAlchemy und listet die Tabellen der Datenbank auf """
    try:
        db = SessionLocal()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Erfolgreich verbunden. Tabellen in der Datenbank:", tables)
        db.close()
    except OperationalError as e:
        print("Fehler bei der Verbindung mit SQLAlchemy:", e)
    except Exception as e:
        print("Allgemeiner Fehler bei SQLAlchemy:", e)

def test_query_users_table():
    """ Testet eine einfache Abfrage in der 'Users'-Tabelle """
    try:
        db = SessionLocal()
        result = db.execute(text('SELECT * FROM "Users" LIMIT 5')).fetchall()
        if result:
            print("Abfrage erfolgreich. Erste 5 Einträge in der Users-Tabelle:")
            for row in result:
                print(row)
        else:
            print("Users-Tabelle ist leer oder Abfrage lieferte keine Ergebnisse.")
        db.close()
    except Exception as e:
        print("Fehler bei der Abfrage der Users-Tabelle:", e)

def main():
    print_system_info()  # Gibt Systeminformationen aus
    print("\n--- Teste Verbindung mit psycopg2 ---")
    test_connection_with_psycopg2()  # Testet die Verbindung mit psycopg2

    print("\n--- Teste Verbindung mit SQLAlchemy ---")
    test_connection_with_sqlalchemy()  # Testet die Verbindung mit SQLAlchemy

    print("\n--- Teste Abfrage in der 'Users'-Tabelle ---")
    test_query_users_table()  # Testet eine Abfrage auf der 'Users'-Tabelle

if __name__ == "__main__":
    main()
