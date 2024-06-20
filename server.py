import socket
import ssl
import threading
from bdd import set_user_status, get_user_status, reset_all_user_statuses
from Cipher import load_private_key, decrypt_message

clients = {}
lock = threading.Lock()


def broadcast_users():
    """Broadcast the list of users and their statuses to all clients."""
    with lock:
        users_status = get_user_status()  # Assume this function queries the database for user statuses
        for client_socket in list(clients.keys()):  # Use list() to iterate over a snapshot of keys
            user_list = [f"{user[0]} ({'Online' if user[1] else 'Offline'})" for user in users_status]
            try:
                client_socket.sendall(f"USERS_LIST {','.join(user_list)}".encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting user list to {clients[client_socket]}: {e}")
                handle_disconnect(client_socket)


def handle_client(conn, addr, private_key):
    """Handle each client connection."""
    print(f"Connected by {addr}")
    with lock:
        clients[conn] = addr
    try:
        while True:
            encrypted_data = conn.recv(1024)
            if not encrypted_data:
                break
            print(f"Encrypted data received from {addr}: {encrypted_data}")
            decrypted_data = decrypt_message(encrypted_data, private_key)
            broadcast(decrypted_data, conn)
    except ssl.SSLError as e:
        print(f"SSL error with {addr}: {e}")
    except socket.error as e:
        print(f"Socket error with {addr}: {e}")
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        handle_disconnect(conn)


def handle_disconnect(conn):
    """Handle disconnection of a client."""
    with lock:
        if conn in clients:
            del clients[conn]
        conn.close()
        print(f"Connection closed: {clients.get(conn, 'Unknown')}")


def update_clients():
    users_list = ', '.join(clients.values())
    broadcast(users_list.encode('utf-8'), "UPDATE_USERS_LIST ")


def broadcast(message, sender_socket):
    """Send a message to all clients except the sender."""
    with lock:
        for client in clients.keys():
            if client != sender_socket:
                try:
                    client.sendall(message.encode('utf-8'))
                except Exception as e:
                    print(f"Failed to send message to {client}: {e}")


def create_server(address):
    """Create and configure the SSL server socket."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="C:\\Users\\tomgo\\ssl\\server.crt",
                            keyfile="C:\\Users\\tomgo\\ssl\\server.key")
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    secure_socket.bind(address)
    secure_socket.listen(5)
    print(f"Server started at {address}, waiting for connections...")
    return secure_socket


def main():
    """Main entry point for the server."""
    private_key = load_private_key()
    secure_socket = create_server(('localhost', 8443))
    try:
        while True:
            conn, addr = secure_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr, private_key)).start()
    except KeyboardInterrupt:
        print("Server terminated by user.")
    finally:
        secure_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    reset_all_user_statuses()
    main()
