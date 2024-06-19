import socket
import threading
import ssl
from Cipher import load_public_key, encrypt_message


class ChatClient:
    def __init__(self, host, port, username, message_received_callback):
        self.host = host
        self.port = port
        self.username = username
        self.message_received_callback = message_received_callback

        # Charger la clé publique
        self.public_key = load_public_key()

        # Créer un contexte SSL
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Connecter au serveur via SSL
        self.sock = context.wrap_socket(socket.socket(socket.AF_INET), server_side=False)
        self.sock.connect((host, port))
        self.sock.sendall(self.encrypt_message(f"LOGIN {username}"))

        # Démarrer le thread pour recevoir des messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def encrypt_message(self, message):
        return encrypt_message(message, self.public_key)

    def send_message(self, message):
        if message:
            encrypted_message = self.encrypt_message(message)
            self.sock.sendall(encrypted_message)

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.sock.recv(1024)
                if encrypted_message:
                    message = encrypted_message.decode('utf-8')
                    if self.message_received_callback:
                        self.message_received_callback(message)
            except Exception as e:
                print("Error receiving message:", e)
                break

    def run(self):
        self.root.mainloop()

    def close_connection(self):
        self.sock.close()


def message_received_callback(message):
    print(f"Message received: {message}")


if __name__ == "__main__":
    host = 'localhost'
    port = 8443
    username = 'user1'

    client = ChatClient(host, port, username, message_received_callback)

    while True:
        message = input("Enter message: ")
        client.send_message(message)
