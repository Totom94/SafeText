import sqlite3


def connect_db():
    """Create a database connection to the SQLite database."""
    try:
        conn = sqlite3.connect('SF.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")


def create_user(pseudo, email, password):
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("INSERT INTO Users (pseudo, email, password, is_connected) VALUES (?, ?, ?, ?)", (pseudo, email, password, 0))
            conn.commit()
            print("User created successfully.")
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def authenticate_user(pseudo, password):
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE pseudo = ? AND password = ?", (pseudo, password))
            user = cur.fetchone()
            if user:
                set_user_status(pseudo, 1)  # Définir l'utilisateur comme connecté
            return user
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
    return None


def init_db():
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT,
                email TEXT,
                password TEXT,
                is_connected INTEGER DEFAULT 0
            )""")
            conn.commit()
            print("Database initialized successfully.")
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        if conn:
            conn.close()


def set_user_status(username, status):
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("UPDATE Users SET is_connected = ? WHERE pseudo = ?", (status, username))
            conn.commit()
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def get_user_status():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, is_connected FROM Users")
    users_status = cursor.fetchall()
    conn.close()
    return users_status


def get_connected_users():
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT pseudo, is_connected FROM Users")
            return cur.fetchall()
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
    return []


if __name__ == "__main__":
    init_db()
