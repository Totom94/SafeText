import sqlite3
import re  # Module pour les expressions régulières
import pyotp

# Expression régulière pour valider l'email
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def connect_db():
    try:
        conn = sqlite3.connect('SF.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")


def update_db():
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("ALTER TABLE Users ADD COLUMN otp_secret TEXT")
            conn.commit()
            print("Database updated successfully.")
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        if "duplicate column name: otp_secret" in str(e):
            print("Column 'otp_secret' already exists.")
        else:
            print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def create_user(pseudo, email, password):
    otp_secret = pyotp.random_base32()
    import re
    # Vérification du format de l'email
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Format d'email incorrect. L'email doit contenir '@' et se terminer par '.com', '.fr', etc.")

    # Vérification de la longueur minimale du mot de passe
    if len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")

    try:
        conn = connect_db()
        if conn is not None:
            # Vérifier si l'utilisateur existe déjà avec le même pseudo ou email
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE pseudo = ? OR email = ?", (pseudo, email))
            existing_user = cur.fetchone()
            if existing_user:
                raise RuntimeError("Un utilisateur avec le même pseudo ou email existe déjà.")

            # Insérer le nouvel utilisateur s'il n'existe pas encore
            cur.execute("INSERT INTO Users (pseudo, email, password, otp_secret, is_connected) VALUES (?, ?, ?, ?, ?)",
                        (pseudo, email, password, otp_secret, 0))
            conn.commit()
            print("User created successfully.")
        else:
            print("Error! cannot create the database connection.")
        return otp_secret
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except RuntimeError as re:
        print(f"RuntimeError: {re}")
    finally:
        if conn:
            conn.close()


def authenticate_user(pseudo, password):
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            # Vérifier si l'utilisateur est déjà connecté
            cur.execute("SELECT * FROM Users WHERE pseudo = ? AND password = ? AND is_connected = 0",
                        (pseudo, password))
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


def get_user_otp_secret(pseudo):
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT otp_secret FROM Users WHERE pseudo = ?", (pseudo,))
            result = cur.fetchone()
            if result:
                return result[0]
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
                pseudo TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT,
                otp_secret TEXT,
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


def reset_all_user_statuses():
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("UPDATE Users SET is_connected = 0")
            conn.commit()
            print("All user statuses reset to offline.")
        else:
            print("Error! cannot create the database connection.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    init_db()
