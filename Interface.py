import tkinter as tk
from tkinter import simpledialog, scrolledtext

def gui_client():
    root = tk.Tk()
    root.title("Secure Chat")

    chat_log = scrolledtext.ScrolledText(root, state='disabled')
    chat_log.grid(row=0, column=0, columnspan=2)

    msg_entry = tk.Entry(root, width=50)
    msg_entry.grid(row=1, column=0)

    def send_msg():
        message = msg_entry.get()
        # Ajouter le code pour envoyer le message au serveur
        msg_entry.delete(0, tk.END)

    send_button = tk.Button(root, text="Send", command=send_msg)
    send_button.grid(row=1, column=1)

    root.mainloop()

if __name__ == '__main__':
    gui_client()


