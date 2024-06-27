import socket
import ssl
import sys
import threading
import subprocess
import os
import logging
from logger import setup_logging
from message_history import log_message
from bdd import get_user_status, reset_all_user_statuses


clients = {}
public_keys = {}
lock = threading.Lock()


def reset_auth_status():
    with open('auth_status.txt', 'w') as f:
        f.write('')


# Démarre le serveur Flask pour OAuth
def start_auth_server():
    auth_server_path = os.path.join(os.path.dirname(__file__), 'auth_server.py')
    subprocess.Popen([sys.executable, auth_server_path])


def handle_public_key(data, client_socket):
    """Traite la réception d'une clé publique d'un client."""
    try:
        parts = data.split(b' ', 2)
        username = parts[1].decode('utf-8')
        public_key_data = parts[2]
        public_keys[username] = public_key_data
        print(f"Clé publique reçue et stockée pour {username}")
    except Exception as e:
        print(f"Échec du traitement de la clé publique : {e}")


def broadcast_users():
    """Diffuse la liste des utilisateurs à tous les clients."""
    with lock:
        users_status = get_user_status()
        for client_socket in list(clients.keys()):
            user_list = [f"{user[0]} ({'Online' if user[1] else 'Offline'})" for user in users_status]
            try:
                client_socket.sendall(f"USERS_LIST {','.join(user_list)}".encode('utf-8'))
            except Exception as e:
                print(f"Erreur lors de la diffusion de la liste des utilisateurs à {clients[client_socket]}: {e}")
                handle_disconnect(client_socket)


def handle_client(conn, addr):
    with lock:
        clients[conn] = addr
    logging.info(f"Connecté par {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data.startswith(b"PUBLIC_KEY"):
                handle_public_key(data, conn)
            else:
                logging.info(f"Données reçues de {addr}: {data}")
                broadcast(data, conn)
    except ssl.SSLError as e:
        logging.error(f"Erreur avec {addr}: {e}")
    except socket.error as e:
        logging.error(f"Erreur de socket avec {addr}: {e}")
    except Exception as e:
        logging.error(f"Erreur avec {addr}: {e}")
    finally:
        logging.info("Connexion fermée.")
        handle_disconnect(conn)


def handle_disconnect(conn):
    with lock:
        if conn in clients:
            del clients[conn]
        conn.close()
        logging.info(f"Connexion fermée : {clients.get(conn, 'Inconnu')}")


def update_clients():
    users_list = ', '.join(clients.values())
    broadcast(users_list.encode('utf-8'), "UPDATE_USERS_LIST ")


def broadcast(message, sender_socket):
    """Diffuse un message à tous les clients sauf à l'expéditeur."""
    with lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.sendall(message)
                except Exception as e:
                    print(f"Échec de l'envoi du message à {clients[client]}: {e}")
                    handle_disconnect(client)


def create_server(address):
    """Crée et configure le socket serveur SSL."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="C:\\Users\\tomgo\\ssl\\server.crt",
                            keyfile="C:\\Users\\tomgo\\ssl\\server.key")
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    secure_socket.bind(address)
    secure_socket.listen(5)
    print(f"Serveur démarré à {address}, en attente de connexions...")
    return secure_socket


def main():
    setup_logging()  # Configure le logging au démarrage du serveur
    logging.info("Démarrage du serveur")

    # Démarre le serveur OAuth dans un thread séparé
    threading.Thread(target=start_auth_server).start()

    secure_socket = create_server(('localhost', 8443))
    try:
        while True:
            conn, addr = secure_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Serveur interrompu par l'utilisateur.")
    finally:
        secure_socket.close()
        print("Socket serveur fermé.")


if __name__ == "__main__":
    reset_all_user_statuses()
    reset_auth_status()
    main()
