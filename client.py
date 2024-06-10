import socket
import ssl


def create_client(host='localhost', port=6789):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="C:/Users/tomgo/ssl/server.crt")  # Chemin vers le certificat du serveur

    context.check_hostname = False  # Désactiver la vérification du nom d'hôte pour les tests
    # context.verify_mode = ssl.CERT_REQUIRED  # Gardez cette ligne pour des environnements de production sécurisés

    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as secure_sock:
            print(f"Connected to {host}:{port}")
            while True:
                message = input("Enter message (type 'exit' to quit): ")
                secure_sock.sendall(message.encode('utf-8'))
                if message.lower() == 'exit':
                    print("Disconnecting from server...")
                    break
                data = secure_sock.recv(1024)
                print(f"Server replied: {data.decode('utf-8')}")


if __name__ == '__main__':
    create_client()
