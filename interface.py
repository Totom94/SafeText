import tkinter as tk
from tkinter import scrolledtext, Button, Label, Frame, Entry, messagebox, Listbox
from pathlib import Path
from client import ChatClient
from bdd import authenticate_user, create_user, get_connected_users, set_user_status
#import threading
#from queue import Queue

def open_chat_window(username):
    global chat_client, messages, entry, user_list
    chat_client = ChatClient('localhost', 6789, username, on_message_received)
    main_window.withdraw()  # Cache la fenêtre principale

    chat_window = tk.Toplevel(main_window)
    chat_window.title("SafeText")
    chat_window.geometry("600x700")

    icon_path = Path(__file__).parent / "C:/Users/tomgo/Downloads/icone.ico"
    if icon_path.exists():
        chat_window.iconbitmap(str(icon_path))

    Label(chat_window, text=f"Connecté en tant que: {username}").pack(pady=10)

    messages = scrolledtext.ScrolledText(chat_window)
    messages.pack(expand=True, fill='both', padx=20, pady=5)

    user_list = Listbox(chat_window, width=30)
    user_list.pack(side="right", fill="y", padx=(0, 20))

    entry_frame = Frame(chat_window)
    entry = Entry(entry_frame)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

    send_button = Button(entry_frame, text="Envoyer", command=send_message)
    send_button.pack(side="right")

    entry_frame.pack(fill="x", padx=20, pady=10)

    chat_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(chat_window, username))  # Gérer la fermeture de la fenêtre
    update_user_list_periodically(chat_window)

    """def update_user_list_periodically():
        update_user_list()
        chat_window.after(5000, update_user_list_periodically)

    threading.Thread(target=update_user_list_periodically, daemon=True).start()



    chat_window.after(5000, update_user_list_periodically)"""


def on_closing(window, username):
    set_user_status(username, 0)  # Définir l'utilisateur comme déconnecté dans la base de données
    chat_client.close_connection()
    window.destroy()
    main_window.deiconify()  # Affiche la fenêtre principale


def on_message_received(message):
    messages.insert(tk.END, f"{message}\n")


def send_message():
    message = entry.get()
    if message:
        chat_client.send_message(message)
        entry.delete(0, tk.END)


def show_login_frame():
    register_frame.pack_forget()
    login_frame.pack()


def show_register_frame():
    login_frame.pack_forget()
    register_frame.pack()


def update_user_list_periodically(window):
    if not window.winfo_exists():
        return
    update_user_list()
    window.after(5000, lambda: update_user_list_periodically(window))


def update_user_list():
    user_list.delete(0, tk.END)
    connected_users = get_connected_users()
    # Trier les utilisateurs : connectés d'abord, puis déconnectés, les deux par ordre alphabétique
    connected_users.sort(key=lambda user: (user[1] == 0, user[0]))
    for user, is_connected in connected_users:
        status = "Connecté" if is_connected else "Hors ligne"
        if is_connected:
            user_list.insert(tk.END, f"{user} ({status})")
        else:
            user_list.insert(tk.END, f"{user} ({status})")
            user_list.itemconfig(tk.END, {'fg': 'grey'})  # Afficher les utilisateurs déconnectés en gris


def login():
    username = username_login_entry.get()
    password = password_login_entry.get()
    # Mock function authenticate_user
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
    # Mock function create_user
    create_user(username, email, password)
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
