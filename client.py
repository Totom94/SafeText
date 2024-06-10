import socket
import ssl

def create_client(host='localhost', port=6789):
    # Création d'un contexte SSL pour le client
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as secure_sock:
            print(f"Connected to {host}:{port}")
            while True:
                message = input("Enter message: ")
                if message.lower() == 'exit':
                    break
                secure_sock.sendall(message.encode('utf-8'))
                data = secure_sock.recv(1024)
                print(f"Server replied: {data.decode('utf-8')}")

if __name__ == '__main__':
    create_client()
