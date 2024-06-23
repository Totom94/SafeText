import tkinter as tk
from tkinter import scrolledtext, Button, Label, Frame, Entry, messagebox, Listbox, PhotoImage
from pathlib import Path
from client import ChatClient
from bdd import authenticate_user, create_user, get_connected_users, set_user_status, get_user_otp_secret
import pyotp
import qrcode


def open_chat_window(username):
    global chat_client, messages, entry, user_list
    chat_client = ChatClient('localhost', 8443, username, on_message_received)
    main_window.withdraw()  # Cache la fenêtre principale

    chat_window = tk.Toplevel(main_window)
    chat_window.title("SafeText")
    chat_window.geometry("600x700")

    icon_path = Path(__file__).parent / "safetext.png"
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

    chat_window.protocol("WM_DELETE_WINDOW",
                         lambda: on_closing(chat_window, username))  # Gérer la fermeture de la fenêtre
    update_user_list_periodically(chat_window)


def on_closing(window, username):
    set_user_status(username, 0)  # Définir l'utilisateur comme déconnecté dans la base de données
    chat_client.close_connection()
    window.destroy()
    main_window.deiconify()


def on_message_received(message):
    messages.insert(tk.END, f"{message}\n")


def send_message():
    message = entry.get()
    if message:
        chat_client.send_message(message)
        entry.delete(0, tk.END)


def show_login_frame():
    register_frame.place_forget()
    login_frame.place(x=440, y=170)
    bare.place(x=510, y=100)


def show_register_frame():
    login_frame.place_forget()
    register_frame.place(x=440, y=170)
    bare.place(x=210, y=100)


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
        messagebox.showerror("Login Info", "Incorrect username or password")


def register():
    username = username_register_entry.get()
    email = email_register_entry.get()
    password = password_register_entry.get()
    # Perform email and password validation
    if not username or not email or not password:
        messagebox.showerror("Register Info", "Username, email, and password are required.")
        return
    if '@' not in email or not email.endswith(('.com', '.fr', '.org')):  # Example validation
        messagebox.showerror("Register Info", "Invalid email format")
        return
    if len(password) < 8:
        messagebox.showerror("Register Info", "Password must be at least 8 characters long")
        return
    otp_secret = create_user(username, email, password)
    totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name="SafeText")
    qr = qrcode.make(totp_uri)
    qr_path = f"{username}_qrcode.png"
    qr.save(qr_path)
    messagebox.showinfo("Register Info", f"Account created successfully. Scan the QR code with your authenticator app.")
    show_login_frame()
    show_qr_code_window(qr_path)


def show_qr_code_window(qr_path):
    qr_window = tk.Toplevel(main_window)
    qr_window.title("Scan QR Code")
    qr_window.geometry("500x500")
    qr_image = tk.PhotoImage(file=qr_path)
    qr_label = tk.Label(qr_window, image=qr_image)
    qr_label.image = qr_image  # Keep a reference to avoid garbage collection
    qr_label.pack(pady=20)
    tk.Button(qr_window, text="OK", command=qr_window.destroy).pack(pady=10)


button_mode = True


def custom():
    global button_mode
    if button_mode:
        theme.config(image=off, bg="white", activebackground="white")
        photo_label.config(image=imgs1)
        main_window.config(bg="white")
        entete.config(bg="white")
        login_button.config(bg="white", fg="blue")
        register_frame.config(bg="aqua")
        login_frame.config(bg="aqua")
        register_button.config(bg="white", fg="blue")
        button_register.config(bg="#32D757")
        button_login.config(bg="#32D757")
        button_mode = False
    else:
        theme.config(image=on, bd=0, activebackground="#545050")
        photo_label.config(image=imgs)
        main_window.config(bg="#545050")
        entete.config(bg="#545050")
        login_button.config(bg="#545050", fg="black")
        login_frame.config(bg='#E9B429')
        register_button.config(bg="#545050", fg="black")
        register_frame.config(bg='#E9B429')
        button_register.config(bg="#ACABAB")
        button_login.config(bg="#ACABAB")
        button_mode = True


# Configuration de la fenêtre principale Tkinter
main_window = tk.Tk()
main_window.title("SafeText")
main_window.geometry("800x600")
main_window.configure(bg='#545050')
main_window.resizable(False, False)
text = tk.StringVar()
icon_path = Path(__file__).parent / "C:/Users/tomgo/Downloads/icone.ico"
if icon_path.exists():
    main_window.iconbitmap(str(icon_path))

# Photo du coin
imgs = PhotoImage(file="login2.png")
imgs1 = PhotoImage(file="login2_light.png")
photo_label = Label(main_window, image=imgs, border=0)
photo_label.place(x=10, y=170)


# CONFIGURATION DU FORMULAIRE

# En-tete du Formulaire
entete = Frame(main_window, width=800, height=150, padx=10, bg="#545050")
entete.pack()

# Changement de theme
on = PhotoImage(file="Dark1.PNG")
off = PhotoImage(file="Light1.PNG")
theme = Button(entete, bg='#545050', image=on, bd=0, activebackground="#545050", command=custom)
theme.place(x=5, y=15)

register_button = Button(entete, border=0, text="Register", bg="#545050", font=("Verdana", 20, "bold"),
                         command=show_register_frame)
register_button.place(x=180, y=50)
login_button = Button(entete, border=0, text="Login", bg="#545050", font=("Verdana", 20, "bold"),
                      command=show_login_frame)
login_button.place(x=500, y=50)
bare = Frame(entete, width=90, height=5, bg='black')


# FENETRE CONNEXION

login_frame = Frame(main_window, width=350, height=390, bg='#E9B429')
login_frame.place(x=440, y=170)


def on_enter(e):
    username_login_entry.delete(0, 'end')


def on_leave(e):
    if username_login_entry.get() == '':
        username_login_entry.insert(0, 'Username')


username_login_entry = Entry(login_frame, width=20, bd=10, fg="gray", border=0, bg='white', font=("Verdana", 18))
username_login_entry.place(x=20, y=80)
username_login_entry.insert(0, 'Username', )
username_login_entry.bind("<FocusIn>", on_enter)
username_login_entry.bind("<FocusOut>", on_leave)
Frame(login_frame, width=295, height=2, bg='black').place(x=20, y=113)


def on_enter(e):
    password_login_entry.delete(0, 'end')


def on_leave(e):
    if password_login_entry.get() == '':
        password_login_entry.insert(0, 'Password')


password_login_entry = Entry(login_frame, width=20, bd=10, border=0, bg='white', font=("Verdana", 18), show='*')
password_login_entry.place(x=20, y=150)
password_login_entry.insert(0, 'Password')
password_login_entry.bind("<FocusIn>", on_enter)
password_login_entry.bind("<FocusOut>", on_leave)
Frame(login_frame, width=295, height=2, bg='black').place(x=20, y=183)


def on_enter(e):
    otp_login_entry.delete(0, 'end')


def on_leave(e):
    if otp_login_entry.get() == '':
        otp_login_entry.insert(0, 'OTP')


otp_login_entry = Entry(login_frame, width=20, bd=10, fg="gray", border=0, bg='white', font=("Verdana", 18))
otp_login_entry.place(x=20, y=220)
otp_login_entry.insert(0, 'OTP')
otp_login_entry.bind("<FocusIn>", on_enter)
otp_login_entry.bind("<FocusOut>", on_leave)
Frame(login_frame, width=295, height=2, bg='black').place(x=20, y=253)
button_login = Button(login_frame, width=40, pady=3, text='Sign Up', bg="#ACABAB", fg='#D99D28', border=0,
                      command=login)
button_login.place(x=25, y=285)


# FENETRE INSCRIPTION

register_frame = tk.Frame(main_window, width=350, height=390, bg='#E9B429')
register_frame.place(x=440, y=170)


def on_enter(e):
    username_register_entry.delete(0, 'end')


def on_leave(e):
    if username_register_entry.get() == '':
        username_register_entry.insert(0, 'Username')


username_register_entry = Entry(register_frame, width=20, bd=10, fg="gray", border=0, bg='white', font=("Verdana", 18))
username_register_entry.place(x=20, y=80)
username_register_entry.insert(0, 'Username', )
username_register_entry.bind("<FocusIn>", on_enter)
username_register_entry.bind("<FocusOut>", on_leave)
Frame(register_frame, width=295, height=2, bg='black').place(x=20, y=113)


def on_enter(e):
    email_register_entry.delete(0, 'end')


def on_leave(e):
    if email_register_entry.get() == '':
        email_register_entry.insert(0, 'E-mail')


email_register_entry = Entry(register_frame, width=20, bd=10, fg="gray", border=0, bg='white', font=("Verdana", 18))
email_register_entry.place(x=20, y=150)
email_register_entry.insert(0, 'E-mail', )
email_register_entry.bind("<FocusIn>", on_enter)
email_register_entry.bind("<FocusOut>", on_leave)
Frame(register_frame, width=295, height=2, bg='black').place(x=20, y=183)


def on_enter(e):
    password_register_entry.delete(0, 'end')


def on_leave(e):
    if password_register_entry.get() == '':
        password_register_entry.insert(0, 'Password')


password_register_entry = Entry(register_frame, width=20, bd=10, border=0, bg='white', font=("Verdana", 18), show='*')
password_register_entry.place(x=20, y=220)
password_register_entry.insert(0, 'Password', )
password_register_entry.bind("<FocusIn>", on_enter)
password_register_entry.bind("<FocusOut>", on_leave)
Frame(register_frame, width=295, height=2, bg='black').place(x=20, y=253)

button_register = Button(register_frame, width=40, pady=3, text='Register', bg="#ACABAB", fg='#D99D28', border=0,
                         command=register)
button_register.place(x=25, y=285)



main_window.mainloop()