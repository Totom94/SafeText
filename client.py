import sys
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

class ChatClient:
    def __init__(self, host, port, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("Chat Room")
        
        self.chat_log = scrolledtext.ScrolledText(self.root, state='disabled', height=20, width=50)
        self.chat_log.grid(row=0, column=0, padx=10, pady=10)
        
        self.users_list = tk.Listbox(self.root, height=20, width=20)
        self.users_list.grid(row=0, column=1, padx=10, pady=10)

        self.msg_entry = tk.Entry(self.root, width=50)
        self.msg_entry.grid(row=1, column=0, padx=10, pady=10)
        
        send_button = tk.Button(self.root, text="Send", command=self.send_msg)
        send_button.grid(row=1, column=1, padx=10, pady=10)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        
        self.name = simpledialog.askstring("Name", "What's your name?", parent=self.root)
        self.sock.sendall(self.name.encode('utf-8'))

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        self.root.mainloop()
        self.users_list_box = tk.Listbox(self.root, height=15, width=30)
        self.users_list_box.grid(row=0, column=1, sticky='nsew', padx=5)

    def send_msg(self):
        message = self.msg_entry.get()
        if message:
            self.sock.sendall(message.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message.startswith("USERS_LIST"):
                    users = message.split(' ')[1]
                    self.update_users_list(users.split(','))
                else:
                    self.chat_log.config(state='normal')
                    self.chat_log.insert(tk.END, message + '\n')
                    self.chat_log.config(state='disabled')
                    self.chat_log.yview(tk.END)
            except:
                break

    def update_users_list(self, users):
        self.users_list_box.delete(0, tk.END)
        for user in users:
            self.users_list_box.insert(tk.END, user)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    ChatClient('localhost', 6789, username)

