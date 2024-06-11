import socket
import ssl
import threading
from BDD import authenticate_user
from ssl_config import load_ssl_context

rooms = {}  # Dictionnaire pour stocker les salles et leurs membres

def handle_client(secure_socket, addr):
    current_room = None
    try:
        # Attendre les données du client
        while True:
            data = secure_socket.recv(1024).decode('utf-8')
            if not data:
                break

            # Commande pour rejoindre une salle
            if data.startswith("/join"):
                _, room_name = data.split()
                if current_room:
                    # Quitter la salle actuelle si elle existe
                    rooms[current_room].remove(secure_socket)
                    send_to_room(current_room, f"{addr} has left the room {current_room}")
                # Ajouter à la nouvelle salle
                rooms[room_name].append(secure_socket)
                current_room = room_name
                send_to_room(current_room, f"{addr} has joined the room {room_name}")

            # Commande pour quitter une salle
            elif data.startswith("/leave"):
                if current_room:
                    rooms[current_room].remove(secure_socket)
                    send_to_room(current_room, f"{addr} has left the room {current_room}")
                    current_room = None

            # Envoyer un message à la salle actuelle
            elif data.startswith("/msg") and current_room:
                _, msg = data.split(maxsplit=1)
                send_to_room(current_room, f"{addr} says: {msg}")
    finally:
        # Fermeture de la connexion
        if current_room and secure_socket in rooms[current_room]:
            rooms[current_room].remove(secure_socket)
            send_to_room(current_room, f"{addr} has left the chat")
        secure_socket.close()

def send_to_room(room_name, message):
    for member in rooms[room_name]:
        try:
            member.sendall(message.encode('utf-8'))
        except:
            rooms[room_name].remove(member)

def create_server(host='localhost', port=6789):
    context = load_ssl_context()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        thread = threading.Thread(target=handle_client, args=(secure_socket, addr))
        thread.start()

if __name__ == '__main__':
    create_server()

