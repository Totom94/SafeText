import socket
import threading
import ssl
import logging

from logger import setup_logging
from cryptography.hazmat.primitives import serialization
from message_history import log_message
from Cipher import load_public_key, load_private_key, encrypt_message, decrypt_message


class ChatClient:
    def __init__(self, host, port, username, message_received_callback):
        setup_logging()
        logging.info(f"Tentative de connexion au serveur {host}:{port} en tant que {username}")
        self.host = host
        self.port = port
        self.username = username
        self.message_received_callback = message_received_callback

        # Chargement des clés pour le chiffrement et le déchiffrement
        self.public_key = load_public_key()
        self.private_key = load_private_key()

        try:
            # Configuration du contexte SSL pour une connexion sécurisée
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.sock = context.wrap_socket(socket.socket(socket.AF_INET), server_side=False)
            self.sock.connect((host, port))

            # Envoi de la clé publique au serveur pour la distribution aux autres clients
            self.sock.sendall(
                f"PUBLIC_KEY {self.username} {self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)}".encode(
                    'utf-8'))

            # Envoi du message de connexion
            self.sock.sendall(self.encrypt_message(f"LOGIN {username}"))
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except ssl.SSLError as e:
            print(f"Erreur SSL : {e}")
            raise
        except socket.error as e:
            print(f"Erreur de socket : {e}")
            raise

    def encrypt_message(self, message):
        """Chiffre le message avec la clé publique."""
        return encrypt_message(message, self.public_key)

    def decrypt_message(self, encrypted_message):
        """Déchiffre le message avec la clé privée."""
        return decrypt_message(encrypted_message, self.private_key)

    def send_message(self, message):
        """Envoie un message chiffré au serveur."""
        try:
            if message:
                encrypted_message = self.encrypt_message(message)
                self.sock.sendall(encrypted_message)
                logging.info(f"Message envoyé : {message}")
                log_message(self.username, message, 'server')
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi du message : {e}")

    def receive_messages(self):
        """Reçoit les messages du serveur et les déchiffre."""
        while True:
            try:
                encrypted_message = self.sock.recv(1024)
                if not encrypted_message:
                    break
                message = self.decrypt_message(encrypted_message)
                log_message('server', message,
                            self.username)  # 'server' ou le nom d'utilisateur expéditeur si applicable
                print(f"Message déchiffré reçu: {message}")  # Affichage du message déchiffré
                if self.message_received_callback:
                    self.message_received_callback(message)
            except ssl.SSLError as e:
                print(f"Erreur SSL : {e}")
                break
            except socket.error as e:
                print(f"Erreur de socket : {e}")
                break
            except Exception as e:
                logging.error(f"Erreur lors de la réception du message : {e}")
                break

    def close_connection(self):
        """Ferme la connexion socket proprement."""
        try:
            self.sock.close()
        except Exception as e:
            print(f"Erreur lors de la fermeture de la connexion : {e}")


def message_received_callback(message):
    print(f"Message reçu: {message}")


if __name__ == "__main__":
    setup_logging()
    host = 'localhost'
    port = 8443
    username = 'user1'
    client = ChatClient(host, port, username, message_received_callback)
    try:
        while True:
            message = input("Entrez un message : ")
            client.send_message(message)
    except KeyboardInterrupt:
        print("Client interrompu par l'utilisateur.")
    finally:
        client.close_connection()
