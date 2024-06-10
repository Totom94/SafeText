import socket
import ssl
from ssl_config import load_ssl_context

def handle_client(secure_socket, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            data = secure_socket.recv(1024)
            if not data:
                print("Connection closed by client")
                break

            message = data.decode('utf-8')
            print(f"Received from {addr}: {message}")

            if message.lower() == 'exit':
                print("Client requested shutdown")
                secure_socket.sendall("Server shutting down connection.".encode('utf-8'))
                break

            response = f"Server received: {message}"
            secure_socket.sendall(response.encode('utf-8'))
    finally:
        secure_socket.close()

def create_server(host='localhost', port=6789):
    context = load_ssl_context()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        handle_client(secure_socket, addr)

if __name__ == '__main__':
    create_server()


