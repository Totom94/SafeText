import socket
import ssl
import threading
from bdd import set_user_status, get_user_status
from Cipher import load_private_key, decrypt_message

clients = {}
lock = threading.Lock()


def broadcast_users():
    with lock:
        users_status = get_user_status()  # Cette fonction doit interroger la base de données pour obtenir le statut
        for client in clients:
            user_list = [f"{user[0]} ({'Online' if user[1] else 'Offline'})" for user in users_status]
            try:
                client.sendall(f"USERS_LIST {','.join(user_list)}".encode('utf-8'))
            except:
                continue


def handle_client(conn, addr, private_key):
    print(f"Connected by {addr}")  # À voir si on garde pour l'aspect sécurité
    with lock:
        clients[conn] = addr  # Assurez-vous d'ajouter le client à un dictionnaire global
    try:
        while True:
            encrypted_data = conn.recv(1024)
            if not encrypted_data:
                break
            print(f"Encrypted data received from {addr}: {encrypted_data}")
            decrypted_data = decrypt_message(encrypted_data, private_key)
            broadcast(decrypted_data, conn)  # Diffuser le message déchiffré aux autres clients
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        conn.close()
        with lock:
            del clients[conn]
        print(f"Connection with {addr} closed.")


def update_clients():
    users_list = ', '.join(clients.values())
    broadcast(users_list.encode('utf-8'), "UPDATE_USERS_LIST ")


def broadcast(message, sender_socket):
    """Send a message to all clients except the sender."""
    with lock:
        for client in clients.keys():
            if client != sender_socket:
                try:
                    client.sendall(message.encode('utf-8'))
                except Exception as e:
                    print(f"Failed to send message to {client}: {e}")


def create_server(address):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="C:\\Users\\tomgo\\ssl\\server.crt",
                            keyfile="C:\\Users\\tomgo\\ssl\\server.key")
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    secure_socket.bind(address)
    secure_socket.listen(5)
    print(f"Server started at {address}, waiting for connections...")
    return secure_socket


def main():
    private_key = load_private_key()
    secure_socket = create_server(('localhost', 8443))
    try:
        while True:
            conn, addr = secure_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr, private_key)).start()
    finally:
        secure_socket.close()


if __name__ == "__main__":
    main()
