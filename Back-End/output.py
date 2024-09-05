import json
import psycopg2

# Funktion, um Benutzer in die Tabelle 'Users' einzufügen
def insert_user_data():
    # Verbindung zur SecureChat-Datenbank herstellen
    conn = psycopg2.connect('postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require')
    cur = conn.cursor()

    # login.json laden
    with open("login.json", "r") as f:
        data = json.load(f)

    # SQL-Abfrage zum Einfügen eines Benutzers in die Haupttabelle 'Users'
    insert_query = '''
    INSERT INTO "Users" (id, username, password, email, registration_date, last_login, ip_address, user_agent, os)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING;
    '''

    # Benutzer aus login.json in die Haupttabelle 'Users' einfügen
    for user in data['users']:
        cur.execute(insert_query, (
            user['id'],  # UUID
            user['username'],
            user['password'],  # Gehe davon aus, dass dies das gehashte Passwort ist
            user['email'],
            user['registration_date'],
            user['last_login'],
            user['ip_address'],
            user['user_agent'],
            user['os']
        ))

    print("Daten in die Haupttabelle 'Users' eingefügt.")

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    cur.close()
    conn.close()
    print("Benutzerdaten erfolgreich in die Datenbank übertragen.")



if __name__ == "__main__":
    insert_user_data()
