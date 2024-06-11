import socket
import ssl
import getpass

def create_client(host='localhost', port=6789):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile="C:/Users/tomgo/ssl/server.crt")  # Chemin vers le certificat du serveur
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    context.check_hostname = False  # Désactiver la vérification du nom d'hôte pour les tests
    # context.verify_mode = ssl.CERT_REQUIRED  # Gardez cette ligne pour des environnements de production sécurisés

    # Connexion sécurisée au serveur
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as secure_sock:
            print(f"Connected to {host}:{port}")

            # Envoi des informations d'authentification
            secure_sock.sendall(f"/login {username} {password}".encode('utf-8'))
            auth_status = secure_sock.recv(1024).decode('utf-8')
            if auth_status == "Authentication successful":
                print("Authentication successful")
            else:
                print("Authentication failed: " + auth_status)
                return

if __name__ == '__main__':
    create_client()
