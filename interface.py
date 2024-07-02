import tkinter as tk
import pyotp
import qrcode
import os
import webbrowser
from tkinter import Button, Label, Frame, Entry, messagebox, Listbox, PhotoImage, Canvas
from pathlib import Path
from client import ChatClient
from bdd import authenticate_user, create_user, set_user_status, get_user_otp_secret, get_connected_users
from auth_server import get_authorized_emails


def check_authentication():
    """Vérifie si l'utilisateur est authentifié en lisant le fichier auth_status.txt"""
    if os.path.exists('auth_status.txt'):
        with open('auth_status.txt', 'r') as f:
            email = f.read().strip()
        if email in get_authorized_emails():
            return email
    return None


def update_user_list_periodically(window, interval=5000):
    """Mettre à jour la liste des utilisateurs toutes les `interval` millisecondes."""
    try:
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
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la liste des utilisateurs : {e}")
    finally:
        window.after(interval, update_user_list_periodically, window, interval)


def open_chat_window(username):
    global chat_client, messages, user_list, chat_bar, envoi, chat_window, icons
    # Créer une référence globale pour les icônes
    icons = {
        "avion": PhotoImage(file="Icon/avion.png"),
        "discuss": PhotoImage(file="Icon/chat.png"),
        "lien1": PhotoImage(file="Icon/lien.png"),
        "lien": PhotoImage(file="Icon/lien1.png"),
        "menu": PhotoImage(file="Icon/menu.png"),
        "param": PhotoImage(file="Icon/param.png"),
        "search": PhotoImage(file="Icon/search.png"),
        "telephone": PhotoImage(file="Icon/telephone.png"),
        "group": PhotoImage(file="Icon/group.png"),
    }
    email = check_authentication()

    def on_closing(window, username):
        """Déconnexion de l'utilisateur"""
        try:
            set_user_status(username, 0)  # Définir l'utilisateur comme déconnecté dans la base de données
            chat_client.close_connection()
            window.destroy()
            main_window.deiconify()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de fermeture de la fenêtre de chat : {e}")

    def on_message_received(message):
        """Afficher le message reçu dans le widget de messages"""
        try:
            Label(messages, bg='gray', text=f"{message}", font=('verdana', 12)).pack(anchor='nw', pady=10)
            Frame(messages).pack()
        except Exception as e:
            print(f"Erreur lors de la réception du message : {e}")

    def send_message():
        """Envoyer le message"""
        try:
            envoi.config(bg='azure')
            message = chat_bar.get()
            if message:
                Label(messages, bg='green', text=f"{message}", font=('verdana', 12)).pack(anchor='ne', pady=10)
                Frame(messages, width=1, bg='red').pack(side='left', fill='x')
                chat_client.send_message(message)
                chat_bar.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec d'envoi du message : {e}")

    def update_user_list(e=None):
        """Mettre à jour la liste des utilisateurs"""
        try:
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
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la liste des utilisateurs : {e}")

    if email:
        try:
            chat_client = ChatClient('localhost', 8443, username, on_message_received)
            main_window.withdraw()  # Cache la fenêtre principale
            chat_window = tk.Toplevel(main_window)
            chat_window.title("SafeText")
            chat_window.geometry("900x750")
            chat_window.config(bg="#f0f0f0")

            # Icone d'entete
            icon_path = Path(__file__).parent / "safetext.ico"
            if icon_path.exists():
                chat_window.iconbitmap(str(icon_path))

            # Barre de Tache
            barre_tache = Frame(chat_window, bg="#d0d0d0", width=700, height=100)
            barre_tache.pack(side="left", fill="both", ipadx=30)
            button1 = Button(barre_tache, image=icons["menu"], bg="#d0d0d0", border=0, activebackground="white")
            button1.pack(side="top", pady=(5, 70))
            button2 = Button(barre_tache, image=icons["discuss"], border=0, bg="#d0d0d0")
            button2.pack(side="top", pady=10)
            button3 = Button(barre_tache, image=icons["telephone"], bg="#d0d0d0", border=0)
            button3.pack(side="top", pady=5)
            button4 = Button(barre_tache, image=icons["group"], bg="#d0d0d0", border=0, activebackground="white")
            button4.pack(side="top", pady=10)
            button5 = Button(barre_tache, image=icons["param"], bg="#d0d0d0", border=0, activebackground="white")
            button5.pack(side="bottom", pady=5)

            # Barre de Profil
            text = tk.StringVar()
            text.set("Texte")

            def on_enter(e):
                search_bar.delete(0, "end")
                search_bar.config(foreground="black")

            acceuil = Frame(chat_window, bg="#f0f0f0")
            acceuil.pack(side="left", fill="both")
            texte = Label(acceuil, textvariable=text, bg="#f0f0f0", foreground="black", font=("Verdana", 20, "bold"))
            texte.pack(side="top", padx=(10, 70), pady=(10, 0))
            search_bar = Entry(acceuil, width=20, border=0, foreground="gray", font=("Verdana", 16))
            search_bar.insert(0, "Search")
            search_bar.bind("<FocusIn>", on_enter)
            search_bar.pack(side="top", padx=(18, 5), pady=(15, 0))
            user_list = Listbox(acceuil, width=30)

            # Barre de Contact
            contact = Frame(chat_window, bg="#d0d0d0", width=750, height=50)
            contact.pack(side="top")
            Label(contact, bg='green', text=f"Connecté en tant que: {username}", font=("Verdana", 15), border=0).pack()

            # Barre de Message
            chat = Frame(chat_window, bg="#d0d0d0", height=300)
            lien = Button(chat, image=icons["lien1"], bg="#d0d0d0", border=0)
            lien.pack(side="left", pady=20, padx=10)
            chat.pack(side="bottom", fill="x", padx=20)

            def on_enter(e):
                chat_bar.delete(0, "end")
                chat_bar.config(foreground="black")

            chat_bar = Entry(chat, border=0, foreground="gray", font=("Verdana", 16))
            chat_bar.insert(0, "Entrer un Message")
            chat_bar.bind("<FocusIn>", on_enter)
            chat_bar.pack(side="top", padx=(10, 20), pady=(15, 0), fill="x")
            envoi = Button(chat, bg='#0078D7', border=0, image=icons["avion"], activebackground="white", command=send_message)
            envoi.pack(side="right", padx=5, anchor='w')

            # Menu de convervation
            mycanvas = Canvas(chat_window, bg='#ffffff')
            mycanvas.pack(fill='both', expand='yes')
            messages = Frame(mycanvas, border=0, bg='#ffffff')
            messages.pack(expand='yes', fill='both', padx=15, pady=15)

            # Barre des utilisateurs
            user_list = Listbox(acceuil, width=30, bg='#f0f0f0', border=0)
            user_list.pack(fill="y", padx=5, pady=10, expand='yes')
            user_list.bind("<Enter>", update_user_list)

            chat_window.protocol("WM_DELETE_WINDOW",
                                 lambda: on_closing(chat_window, username))  # Gérer la fermeture de la fenêtre
            update_user_list_periodically(chat_window)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec d'ouverture de la fenêtre de chat : {e}")
    else:
        messagebox.showerror("Accès refusé", "Vous devez d'abord vous authentifier.")
        webbrowser.open("http://localhost:5000")


def show_login_frame():
    """Afficher le frame de connexion"""
    register_frame.place_forget()
    login_frame.place(x=440, y=170)
    bare.place(x=510, y=100)


def show_register_frame():
    """Afficher le frame d'inscription"""
    login_frame.place_forget()
    register_frame.place(x=440, y=170)
    bare.place(x=210, y=100)


def login():
    """Login"""
    try:
        username = username_login_entry.get()
        password = password_login_entry.get()
        otp = otp_login_entry.get()
        user = authenticate_user(username, password)
        if user:
            otp_secret = get_user_otp_secret(username)
            totp = pyotp.TOTP(otp_secret)
            if totp.verify(otp):
                messagebox.showinfo("Info de connexion", "Connexion réussie")
                open_chat_window(username)
            else:
                messagebox.showerror("Info de connexion", "OTP incorrect")
        else:
            messagebox.showerror("Info de connexion", "Nom d'utilisateur ou mot de passe incorrect")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de la connexion : {e}")


def register():
    """Création de l'utilisateur dans la base de données"""
    try:
        username = username_register_entry.get()
        email = email_register_entry.get()
        password = password_register_entry.get()

        # Vérification de la validité de l'email et du mot de passe
        if not username or not email or not password or password == 'Password':
            messagebox.showerror("Informations d'inscription", "Nom d'utilisateur, email et un mot de passe valide "
                                                               "sont requis.")
            return
        if '@' not in email or not email.endswith(('.com', '.fr', '.org')):  # Validation de l'email (exemple)
            messagebox.showerror("Informations d'inscription", "Format d'email invalide")
            return
        if len(password) < 8:
            messagebox.showerror("Informations d'inscription", "Le mot de passe doit comporter au moins 8 caractères")
            return

        # Création de l'utilisateur dans la base de données
        otp_secret = create_user(username, email, password)
        totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name="SafeText")
        qr = qrcode.make(totp_uri)
        qr_path = f"{username}_qrcode.png"
        qr.save(qr_path)
        messagebox.showinfo("Informations d'inscription", f"Compte créé avec succès. Scannez le code QR avec votre "
                                                          f"application d'authentification.")
        show_login_frame()
        show_qr_code_window(qr_path)
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de l'inscription : {e}")


def show_qr_code_window(qr_path):
    """Création de la fenêtre de QR code"""
    try:
        qr_window = tk.Toplevel(main_window)
        qr_window.title("Scan QR Code")
        qr_window.geometry("500x500")
        qr_image = tk.PhotoImage(file=qr_path)
        qr_label = tk.Label(qr_window, image=qr_image)
        qr_label.image = qr_image  # Keep a reference to avoid garbage collection
        qr_label.pack(pady=20)
        tk.Button(qr_window, text="OK", command=qr_window.destroy).pack(pady=10)
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec d'affichage de la fenêtre du code QR : {e}")


button_mode = True


def custom():
    """Mode sombre"""
    global button_mode
    try:
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
    except Exception as e:
        print(f"Erreur lors du changement de thème : {e}")


# Vérifier l'authentification avant de lancer l'application principale
email = check_authentication()
if email:
    # Configuration de la fenêtre principale Tkinter
    main_window = tk.Tk()
    main_window.title("SafeText")
    main_window.geometry("800x600")
    main_window.configure(bg='#545050')
    main_window.resizable(False, False)
    text = tk.StringVar()
    icon_path = Path(__file__).parent / "safetext.ico"
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


    username_register_entry = Entry(register_frame, width=20, bd=10, fg="gray", border=0, bg='white',
                                    font=("Verdana", 18))
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


    password_register_entry = Entry(register_frame, width=20, bd=10, border=0, bg='white', font=("Verdana", 18),
                                    show='*')
    password_register_entry.place(x=20, y=220)
    password_register_entry.insert(0, 'Password', )
    password_register_entry.bind("<FocusIn>", on_enter)
    password_register_entry.bind("<FocusOut>", on_leave)
    Frame(register_frame, width=295, height=2, bg='black').place(x=20, y=253)

    button_register = Button(register_frame, width=40, pady=3, text='Register', bg="#ACABAB", fg='#D99D28', border=0,
                             command=register)
    button_register.place(x=25, y=285)

    main_window.mainloop()
else:
    webbrowser.open("http://localhost:5000")
    messagebox.showinfo("Authentification requise", "Veuillez vous authentifier via la page web avant d'accéder au "
                                                    "chat.")
