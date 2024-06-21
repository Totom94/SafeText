from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import os

# Chemins globaux des clés
PRIVATE_KEY_PATH = "C:\\Users\\tomgo\\ssl\\private_key.pem"
PUBLIC_KEY_PATH = "C:\\Users\\tomgo\\ssl\\public_key.pem"


def load_public_key():
    try:
        with open(PUBLIC_KEY_PATH, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        print("Clé publique chargée.")
        return public_key
    except Exception as e:
        print(f"Erreur lors du chargement de la clé publique : {e}")
        raise  # Re-lève l'exception pour une gestion ultérieure si nécessaire


def load_private_key():
    try:
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None)
        print("Clé privée chargée.")
        return private_key
    except Exception as e:
        print(f"Erreur lors du chargement de la clé privée : {e}")
        raise  # Re-lève l'exception pour une gestion ultérieure si nécessaire


def encrypt_message(message, public_key):
    try:
        encrypted = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(f"Message encrypté : {encrypted}")
        return encrypted
    except Exception as e:
        print(f"Erreur lors du chiffrement du message : {e}")
        raise  # Re-lève l'exception pour une gestion ultérieure si nécessaire


def decrypt_message(encrypted_message, private_key):
    try:
        decrypted = private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Erreur lors du déchiffrement du message : {e}")
        raise  # Re-lève l'exception pour une gestion ultérieure si nécessaire


if __name__ == "__main__":
    try:
        public_key = load_public_key()
        private_key = load_private_key()

        message = "Hello, world!"
        encrypted_message = encrypt_message(message, public_key)
        print(f"Message chiffré : {encrypted_message}")

        decrypted_message = decrypt_message(encrypted_message, private_key)
        print(f"Message déchiffré : {decrypted_message}")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
