import tkinter as tk
from tkinter import scrolledtext, Button, Label, Frame, Entry, messagebox, Listbox
from pathlib import Path
from client import ChatClient
from bdd import authenticate_user, create_user, get_connected_users, set_user_status, get_user_otp_secret
import pyotp
import qrcode


def open_chat_window(username):
    global chat_client, messages, entry, user_list
    try:
        chat_client = ChatClient('localhost', 8443, username, on_message_received)
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
        return

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


def on_closing(window, username):
    try:
        set_user_status(username, 0)  # Définir l'utilisateur comme déconnecté dans la base de données
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update status on logout: {e}")
    chat_client.close_connection()
    window.destroy()
    main_window.deiconify()


def on_message_received(message):
    messages.insert(tk.END, f"{message}\n")


def send_message():
    message = entry.get()
    if message:
        try:
            chat_client.send_message(message)
            entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {e}")


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
    otp = otp_login_entry.get()
    try:
        user = authenticate_user(username, password)
        if user:
            otp_secret = get_user_otp_secret(username)
            totp = pyotp.TOTP(otp_secret)
            if totp.verify(otp):
                messagebox.showinfo("Login Info", "Successful Login")
                open_chat_window(username)
            else:
                messagebox.showerror("Login Info", "Incorrect OTP")
        else:
            messagebox.showerror("Login Info", "Incorrect username/password or user already connected")
    except Exception as e:
        messagebox.showerror("Login Error", f"Login failed: {e}")


def register():
    username = username_register_entry.get()
    email = email_register_entry.get()
    password = password_register_entry.get()
    try:
        otp_secret = create_user(username, email, password)
        totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name="SafeText")
        qr = qrcode.make(totp_uri)
        qr_path = f"{username}_qrcode.png"
        qr.save(qr_path)
        messagebox.showinfo("Register Info",
                            f"Account created successfully. Scan the QR code with your authenticator app.")
        show_login_frame()
        show_qr_code_window(qr_path)
    except Exception as e:
        messagebox.showerror("Registration Error", f"Registration failed: {e}")


def show_qr_code_window(qr_path):
    qr_window = tk.Toplevel(main_window)
    qr_window.title("Scan QR Code")
    qr_window.geometry("500x500")
    qr_image = tk.PhotoImage(file=qr_path)
    qr_label = tk.Label(qr_window, image=qr_image)
    qr_label.image = qr_image  # Keep a reference to avoid garbage collection
    qr_label.pack(pady=20)
    tk.Button(qr_window, text="OK", command=qr_window.destroy).pack(pady=10)


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
tk.Label(login_frame, text="OTP:").pack()  # Ajouter le champ OTP
otp_login_entry = tk.Entry(login_frame)
otp_login_entry.pack()
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
