import sqlite3

DATABASE = "internships.db"


def getConnection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection

def initializeDatabase():
    connection = getConnection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            url TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER NOT NULL,
            internship_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('saved', 'hidden')),

            PRIMARY KEY (user_id, internship_id),

            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (internship_id) REFERENCES internships(id)
        );
    """)

    connection.commit()
    connection.close()

def saveInternshipsToDatabase(internships):
    connection = getConnection()

    for internship in internships:
        connection.execute("""
            INSERT OR IGNORE INTO internships
            (company, title, location, url)
            VALUES (?, ?, ?, ?)
        """, (
            internship["company"],
            internship["title"],
            internship["location"],
            internship["url"]
        ))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    initializeDatabase()
    print("Database initialized successfully!")