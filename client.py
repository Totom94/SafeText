import socket
import threading


class ChatClient:
    def __init__(self, host, port, username, message_received_callback):
        self.host = host
        self.port = port
        self.username = username
        self.message_received_callback = message_received_callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.sendall(f"LOGIN {username}".encode('utf-8'))
        threading.Thread(target=self.receive_messages, daemon=True).start()

    """def setup_widgets(self):
        self.messages = scrolledtext.ScrolledText(self.root)
        self.messages.pack()
        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.bind("<Return>", self.send_message)"""

    def send_message(self, message):
        if message:
            self.sock.sendall(message.encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if self.message_received_callback:
                    self.message_received_callback(message)
            except Exception as e:
                print("Error receiving message:", e)
                break

    def run(self):
        self.root.mainloop()

    def close_connection(self):
        self.sock.close()
