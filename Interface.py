import socket
import ssl
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
from ssl_config import load_ssl_context


class ChatClient:
    def __init__(self, host='localhost', port=6789):
        self.host = host
        self.port = port
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations(cafile="C:/Users/tomgo/ssl/server.crt")  # Chemin vers le certificat du serveur
        self.context.check_hostname = False  # Désactiver la vérification du nom d'hôte pour les tests
        self.context.verify_mode = ssl.CERT_REQUIRED

        self.sock = None
        self.secure_sock = None

        self.root = tk.Tk()
        self.root.title("Secure Chat")

        self.chat_log = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_log.grid(row=0, column=0, columnspan=2)

        self.msg_entry = tk.Entry(self.root, width=50)
        self.msg_entry.grid(row=1, column=0)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_msg)
        self.send_button.grid(row=1, column=1)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self.secure_sock = self.context.wrap_socket(self.sock, server_hostname=self.host)
            self.print_to_log("Connected to server.")
        except Exception as e:
            self.print_to_log(f"Connection failed: {e}")

    def send_msg(self):
        message = self.msg_entry.get()
        if message.lower() == 'exit':
            self.disconnect_from_server()
            self.root.quit()
            return

        self.secure_sock.sendall(message.encode('utf-8'))
        self.msg_entry.delete(0, tk.END)
        self.print_to_log(f"You: {message}")

        data = self.secure_sock.recv(1024)
        if data:
            self.print_to_log(f"Server: {data.decode('utf-8')}")

    def print_to_log(self, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + '\n')
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def disconnect_from_server(self):
        if self.secure_sock:
            self.secure_sock.sendall("exit".encode('utf-8'))
            self.secure_sock.close()
        if self.sock:
            self.sock.close()
        self.print_to_log("Disconnected from server.")

    def on_closing(self):
        self.disconnect_from_server()
        self.root.quit()

    def run(self):
        self.root.mainloop()

def send_msg(self):
    def do_send():
        message = self.msg_entry.get()
        if message.lower() == 'exit':
            self.disconnect_from_server()
            self.root.quit()
            return

        try:
            self.secure_sock.sendall(message.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)
            data = self.secure_sock.recv(1024)
            if data:
                self.print_to_log(f"Server: {data.decode('utf-8')}")
        except Exception as e:
            self.print_to_log(f"Error sending message: {e}")
            self.disconnect_from_server()

    threading.Thread(target=do_send).start()

if __name__ == '__main__':
    client = ChatClient()
    client.run()


