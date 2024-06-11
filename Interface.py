import socket
import ssl
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
from pathlib import Path

class ChatClient:
    def __init__(self, host='localhost', port=6789):
        self.host = host
        self.port = port
        self.context = self.load_ssl_context()

        self.root = tk.Tk()
        self.root.title("Secure Chat")

        self.chat_log = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_log.grid(row=0, column=0, columnspan=2)

        self.pseudo_entry = tk.Entry(self.root, width=50)
        self.pseudo_entry.grid(row=1, column=0, columnspan=2)

        self.email_entry = tk.Entry(self.root, width=50)
        self.email_entry.grid(row=2, column=0, columnspan=2)

        self.password_entry = tk.Entry(self.root, show="*", width=50)
        self.password_entry.grid(row=3, column=0, columnspan=2)

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.grid(row=4, column=0)

        self.register_button = tk.Button(self.root, text="Register", command=self.register)
        self.register_button.grid(row=4, column=1)

        self.msg_entry = tk.Entry(self.root, width=50)
        self.msg_entry.grid(row=5, column=0)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_msg)
        self.send_button.grid(row=5, column=1)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.connect_to_server()  # Cette ligne devrait être après l'initialisation complète
        self.root.mainloop()

    def load_ssl_context(self):
        home_dir = Path.home()
        ssl_dir = home_dir / "ssl"

        key_path = ssl_dir / "server.key"
        cert_path = ssl_dir / "server.crt"

        if not key_path.exists() or not cert_path.exists():
            raise FileNotFoundError(f"Les fichiers SSL n'ont pas été trouvés dans {ssl_dir}")

        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # Ignore SSL certificate verification

        return ssl_context

    def connect_to_server(self):
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self.secure_sock = self.context.wrap_socket(self.sock, server_hostname=self.host)
            self.print_to_log("Connected to server.")
        except Exception as e:
            self.print_to_log(f"Connection failed: {e}")

    def login(self):
        pseudo = self.pseudo_entry.get()
        password = self.password_entry.get()
        self.secure_sock.sendall(f"/login {pseudo} {password}".encode('utf-8'))

    def register(self):
        pseudo = self.pseudo_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        self.secure_sock.sendall(f"/register {pseudo} {email} {password}".encode('utf-8'))

    def send_msg(self):
        message = self.msg_entry.get()
        self.secure_sock.sendall(message.encode('utf-8'))
        self.msg_entry.delete(0, tk.END)

    def print_to_log(self, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + '\n')
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def disconnect_from_server(self):
        self.secure_sock.sendall("exit".encode('utf-8'))
        self.secure_sock.close()

    def on_closing(self):
        self.disconnect_from_server()
        self.root.quit()

    def run(self):
        self.connect_to_server()
        self.root.mainloop()

if __name__ == '__main__':
    client = ChatClient()
    client.run()
