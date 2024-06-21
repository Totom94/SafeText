import socket
import threading
import ssl
from cryptography.hazmat.primitives import serialization
from Cipher import load_public_key, load_private_key, encrypt_message, decrypt_message


class ChatClient:
    def __init__(self, host, port, username, message_received_callback):
        self.host = host
        self.port = port
        self.username = username
        self.message_received_callback = message_received_callback

        # Charger les clés publique et privée
        self.public_key = load_public_key()
        self.private_key = load_private_key()

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            self.sock = context.wrap_socket(socket.socket(socket.AF_INET), server_side=False)
            self.sock.connect((host, port))

            # Envoyer la clé publique au serveur pour distribution
            self.sock.sendall(
                f"PUBLIC_KEY {self.username} {self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)}".encode(
                    'utf-8'))

            self.sock.sendall(self.encrypt_message(f"LOGIN {username}"))

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except ssl.SSLError as e:
            print(f"SSL error occurred: {e}")
            raise
        except socket.error as e:
            print(f"Socket error occurred: {e}")
            raise

    def encrypt_message(self, message):
        return encrypt_message(message, self.public_key)

    def decrypt_message(self, encrypted_message):
        return decrypt_message(encrypted_message, self.private_key)

    def send_message(self, message):
        try:
            if message:
                encrypted_message = self.encrypt_message(message)
                self.sock.sendall(encrypted_message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.sock.recv(1024)
                if not encrypted_message:
                    break
                message = self.decrypt_message(encrypted_message)
                if self.message_received_callback:
                    self.message_received_callback(message)
            except ssl.SSLError as e:
                print(f"SSL error occurred: {e}")
                break
            except socket.error as e:
                print(f"Socket error occurred: {e}")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def close_connection(self):
        try:
            self.sock.close()
        except Exception as e:
            print(f"Error closing connection: {e}")


def message_received_callback(message):
    print(f"Message received: {message}")


if __name__ == "__main__":
    host = 'localhost'
    port = 8443
    username = 'user1'
    client = ChatClient(host, port, username, message_received_callback)
    try:
        while True:
            message = input("Enter message: ")
            client.send_message(message)
    except KeyboardInterrupt:
        print("Client terminated by user.")
    finally:
        client.close_connection()
