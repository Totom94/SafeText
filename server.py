import socket
import threading
from bdd import set_user_status, get_user_status

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


def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established.")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"No more data from {addr}.")
                break
            print(f"Received from {addr}: {message}")
            broadcast(message, f"{clients[client_socket]}: ")
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        client_socket.close()
        del clients[client_socket]
        print(f"Connection with {addr} closed.")




def update_clients():
    users_list = ', '.join(clients.values())
    broadcast(users_list.encode('utf-8'), "UPDATE_USERS_LIST ")

def broadcast(message, prefix=""):
    with lock:
        for client in clients:
            try:
                client.sendall(prefix.encode('utf-8') + message)
                print(f"Broadcasting message to {client}: {prefix + message.decode('utf-8')}")  # Affiche les messages diffusés
            except Exception as e:
                print(f"Failed to broadcast to {client}: {e}")  # Affiche les erreurs
                continue


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6789))
    server_socket.listen(5)
    clients = []
    try:
        while True:
            conn, addr = server_socket.accept()
            clients.append(conn)
            threading.Thread(target=client_thread, args=(conn, addr, clients)).start()
    finally:
        server_socket.close()


def client_thread(conn, addr, clients):
    try:
        while True:
            message = conn.recv(1024).decode('utf-8')
            print(f"Received {message} from {addr}")
            for c in clients:
                if c != conn:
                    c.sendall(message.encode('utf-8'))
    finally:
        conn.close()

if __name__ == '__main__':
    start_server()

