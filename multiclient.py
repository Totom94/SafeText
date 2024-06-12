import socket
import threading

def client_handler(client_socket, client_address):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Message from {client_address}: {message}")
                # Echo the message back to client
                client_socket.sendall(message.encode('utf-8'))
            else:
                break
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6789))
    server_socket.listen()
    print("Server is listening on port 6789...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected to {client_address}")
            thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
            thread.start()
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()
