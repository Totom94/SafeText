import socket
import ssl
from ssl_config import load_ssl_context  # Assurez-vous d'avoir ssl_config.py configuré

def create_server(host='localhost', port=6789):
    context = load_ssl_context()  # Utilisez la fonction load_ssl_context pour charger le contexte SSL

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        try:
            print(f"Connected by {addr}")
            while True:
                data = secure_socket.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode('utf-8')}")
                secure_socket.sendall(data)
        finally:
            secure_socket.close()

if __name__ == '__main__':
    create_server()
