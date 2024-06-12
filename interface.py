import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from bdd import authenticate_user, create_user
import subprocess
import sys
from pathlib import Path

def show_login_frame():
    register_frame.pack_forget()
    login_frame.pack()

def show_register_frame():
    login_frame.pack_forget()
    register_frame.pack()

def open_chat_window(username):
    # Cacher la fenêtre principale et ouvrir une fenêtre de chat
    main_window.withdraw()
    chat_window = tk.Toplevel(main_window)
    chat_window.title(f"Chat Room - {username}")
    chat_window.geometry("400x400")

    # Zone de chat pour afficher les messages
    chat_log = scrolledtext.ScrolledText(chat_window, state='disabled', height=15, width=50)
    chat_log.pack(pady=10)

    # Entrée de message
    msg_entry = tk.Entry(chat_window, width=40)
    msg_entry.pack(pady=5)

    # Bouton pour envoyer des messages
    send_button = tk.Button(chat_window, text="Send", command=lambda: send_message(chat_log, msg_entry))
    send_button.pack()

    # Gestion de la fermeture de la fenêtre de chat
    chat_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(chat_window))


def send_message(chat_log, msg_entry):
    message = msg_entry.get()
    if message:
        # Simuler l'envoi et la réception de messages
        chat_log.config(state='normal')
        chat_log.insert(tk.END, message + '\n')
        chat_log.config(state='disabled')
        chat_log.yview(tk.END)
        msg_entry.delete(0, tk.END)

def on_closing(chat_window):
    # Réafficher la fenêtre principale lorsque la fenêtre de chat est fermée
    chat_window.destroy()
    main_window.deiconify()

def login():
    username = username_login_entry.get()
    password = password_login_entry.get()
    user = authenticate_user(username, password)
    if user:
        messagebox.showinfo("Login Info", "Successful Login")
        open_chat_window(username)
    else:
        messagebox.showerror("Login Info", "Incorrect username or password")


def register():
    username = username_register_entry.get()
    email = email_register_entry.get()
    password = password_register_entry.get()
    create_user(username, email, password)
    messagebox.showinfo("Register Info", "Account created successfully")
    show_login_frame()

main_window = tk.Tk()
main_window.title("SafeText")
main_window.geometry("800x600")  # Augmenter la taille de la fenêtre
icon_path = Path(__file__).parent / "C:/Users/tomgo/Downloads/icone.ico"
if icon_path.exists():
    main_window.iconbitmap(str(icon_path))

# Configuration de la fenêtre de connexion
login_frame = tk.Frame(main_window)
tk.Label(login_frame, text="Username:").pack()
username_login_entry = tk.Entry(login_frame)
username_login_entry.pack()
tk.Label(login_frame, text="Password:").pack()
password_login_entry = tk.Entry(login_frame, show='*')
password_login_entry.pack()
tk.Button(login_frame, text="Login", command=login).pack()
tk.Button(login_frame, text="Register", command=show_register_frame).pack()

# Configuration de la fenêtre d'inscription
register_frame = tk.Frame(main_window)
tk.Label(register_frame, text="Username:").pack()
username_register_entry = tk.Entry(register_frame)
username_register_entry.pack()
tk.Label(register_frame, text="Email:").pack()
email_register_entry = tk.Entry(register_frame)
email_register_entry.pack()
tk.Label(register_frame, text="Password:").pack()
password_register_entry = tk.Entry(register_frame, show='*')
password_register_entry.pack()
tk.Button(register_frame, text="Register", command=register).pack()
tk.Button(register_frame, text="Back to Login", command=show_login_frame).pack()

# Ajout d'un label pour afficher le nom d'utilisateur connecté
user_label = tk.Label(main_window)


login_frame.pack()

main_window.mainloop()
