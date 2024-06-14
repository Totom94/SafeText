import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
from client import ChatClient
from bdd import authenticate_user, create_user

def open_chat_window(username):
    chat_client = ChatClient('localhost', 6789, username)
    chat_client.run()

def show_login_frame():
    register_frame.pack_forget()
    login_frame.pack()

def show_register_frame():
    login_frame.pack_forget()
    register_frame.pack()

def login():
    username = username_login_entry.get()
    password = password_login_entry.get()
    # Mock function authenticate_user
    user = authenticate_user(username, password)  # Replace with actual implementation
    if user:
        messagebox.showinfo("Login Info", "Successful Login")
        open_chat_window(username)
    else:
        messagebox.showerror("Login Info", "Incorrect username or password")

def register():
    username = username_register_entry.get()
    email = email_register_entry.get()
    password = password_register_entry.get()
    # Mock function create_user
    create_user(username, email, password)  # Replace with actual implementation
    messagebox.showinfo("Register Info", "Account created successfully")
    show_login_frame()

# Configuration de la fenêtre principale Tkinter

main_window = tk.Tk()
main_window.title("SafeText")
main_window.geometry("800x600")

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

login_frame.pack()

main_window.mainloop()
