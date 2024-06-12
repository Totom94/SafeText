import sqlite3

def connect_db():
    """Create a database connection to the SQLite database."""
    try:
        conn = sqlite3.connect('SF.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")

def create_user(pseudo, email, password):
    """
    Create a new user in the Users table.
    :param pseudo: username of the user
    :param email: email of the user
    :param password: password of the user
    """
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("INSERT INTO Users (pseudo, email, password) VALUES (?, ?, ?)", (pseudo, email, password))
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
    """
    Authenticate a user from the Users table.
    :param pseudo: username of the user
    :param password: password of the user
    """
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE pseudo = ? AND password = ?", (pseudo, password))
            user = cur.fetchone()
            return user
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def init_db():
    """Create the Users table in the database if it doesn't already exist."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT,
                email TEXT,
                password TEXT
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
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET is_connected = ? WHERE username = ?", (status, username))
    conn.commit()
    conn.close()

def get_user_status():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, is_connected FROM Users")
    users_status = cursor.fetchall()
    conn.close()
    return users_status

if __name__ == "__main__":
    init_db()
