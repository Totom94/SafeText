import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from bdd import authenticate_user, create_user
import subprocess
import sys

def show_login_frame():
    register_frame.pack_forget()
    login_frame.pack()

def show_register_frame():
    login_frame.pack_forget()
    register_frame.pack()

def open_chat_window(username):
    main_window.destroy()
    subprocess.Popen([sys.executable, 'client.py', username])

    def on_closing(chat_window):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            chat_window.destroy()
            main_window.destroy()  # Ceci va fermer complètement l'application

def send_message(chat_log, msg_entry):
    message = msg_entry.get()
    if message:
        # Afficher le message dans la zone de chat
        chat_log.config(state='normal')
        chat_log.insert(tk.END, message + '\n')
        chat_log.config(state='disabled')
        chat_log.yview(tk.END)
        msg_entry.delete(0, tk.END)

def login():
    username = username_login_entry.get()
    password = password_login_entry.get()
    user = authenticate_user(username, password)
    if user:
        messagebox.showinfo("Login Info", "Successful Login")
        open_chat_window(username)  # Passer le nom d'utilisateur
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
main_window.title("Secure Chat Login")

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

login_frame.pack()

main_window.mainloop()
