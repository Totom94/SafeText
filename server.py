import socket
import threading

clients = {}
lock = threading.Lock()

def broadcast_users():
    users_list = [clients[client] for client in clients]  # Liste des noms d'utilisateur
    for client in clients:
        try:
            client.sendall(f"USERS_LIST {','.join(users_list)}".encode('utf-8'))
        except:
            continue
        
def handle_client(client_socket, addr):
    name = client_socket.recv(1024).decode('utf-8')
    clients[client_socket] = name
    broadcast_users()

    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(message, name + ": ")
    finally:
        del clients[client_socket]
        broadcast_users()
        client_socket.close()

def update_clients():
    users_list = ', '.join(clients.values())
    broadcast(users_list.encode('utf-8'), "UPDATE_USERS_LIST ")

def broadcast(message, prefix=""):
    with lock:
        for client in clients:
            client.sendall(prefix.encode('utf-8') + message)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6789))
    server_socket.listen()
    print("Server listening on port 6789...")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()

