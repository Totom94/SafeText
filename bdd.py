import sqlite3
import re  # Module pour les expressions régulières
import pyotp
import bcrypt  # Module pour le hachage sécurisé des mots de passe

# Expression régulière pour valider l'email
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def connect_db():
    """Établit une connexion à la base de données SQLite."""
    try:
        conn = sqlite3.connect('SF.db')
        return conn
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        raise


def update_db():
    """Met à jour la base de données en ajoutant une colonne otp_secret."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("ALTER TABLE Users ADD COLUMN otp_secret TEXT")
            conn.commit()
            print("Base de données mise à jour avec succès.")
        else:
            print("Erreur ! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        if "duplicate column name: otp_secret" in str(e):
            print("La colonne 'otp_secret' existe déjà.")
        else:
            print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()


def create_user(pseudo, email, password):
    """Crée un nouvel utilisateur dans la base de données."""
    import re
    otp_secret = pyotp.random_base32()

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

            # Générer un sel aléatoire
            salt = bcrypt.gensalt()

            # Hacher le mot de passe avec le sel
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

            # Insérer le nouvel utilisateur s'il n'existe pas encore
            cur.execute("INSERT INTO Users (pseudo, email, password, otp_secret, is_connected) VALUES (?, ?, ?, ?, ?)",
                        (pseudo, email, hashed_password.decode('utf-8'), otp_secret, 0))
            conn.commit()
            print("Utilisateur créé avec succès.")
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
        return otp_secret
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    except ValueError as ve:
        print(f"Erreur de valeur : {ve}")
        raise
    except RuntimeError as re:
        print(f"Erreur d'exécution : {re}")
        raise
    finally:
        if conn:
            conn.close()


def authenticate_user(pseudo, password):
    """Authentifie un utilisateur et renvoie ses informations si l'authentification réussit."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            # Vérifier si l'utilisateur est déjà connecté
            cur.execute("SELECT * FROM Users WHERE pseudo = ?", (pseudo,))
            user = cur.fetchone()
            if user:
                # Vérifier si le mot de passe correspond
                hashed_password = user[3]  # Récupérer le mot de passe haché depuis la base de données
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    set_user_status(pseudo, 1)  # Définir l'utilisateur comme connecté
                    return user
            else:
                print("Utilisateur non trouvé.")
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()
    return None


def get_user_otp_secret(pseudo):
    """Récupère le secret OTP pour l'utilisateur spécifié."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT otp_secret FROM Users WHERE pseudo = ?", (pseudo,))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                print("Utilisateur non trouvé.")
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()
    return None


def init_db():
    """Initialise la base de données avec les tables Users et OTPs."""
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
            print("Base de données initialisée avec succès.")
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite lors de l'initialisation de la base de données : {e}")
        raise
    finally:
        if conn:
            conn.close()


def set_user_status(username, status):
    """Définition du statut de connexion d'un utilisateur."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("UPDATE Users SET is_connected = ? WHERE pseudo = ?", (status, username))
            conn.commit()
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_user_status():
    """Retourne une liste de tous les utilisateurs ainsi que leur statut de connexion."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT pseudo, is_connected FROM Users")
            return cur.fetchall()
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()
    return []


def get_connected_users():
    """Retourne une liste de tous les utilisateurs connectés."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT pseudo, is_connected FROM Users WHERE is_connected = 1")
            return cur.fetchall()
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()
    return []


def reset_all_user_statuses():
    """Réinitialise le statut de tous les utilisateurs à hors ligne."""
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("UPDATE Users SET is_connected = 0")
            conn.commit()
            print("Tous les statuts d'utilisateur ont été réinitialisés à hors ligne.")
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_all_users():
    try:
        conn = connect_db()
        if conn is not None:
            cur = conn.cursor()
            cur.execute("SELECT pseudo, is_connected FROM Users")
            return cur.fetchall()
        else:
            print("Erreur! Impossible de créer la connexion à la base de données.")
    except sqlite3.Error as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        if conn:
            conn.close()
    return []


if __name__ == "__main__":
    init_db()


