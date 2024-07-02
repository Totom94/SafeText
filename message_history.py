import os
import threading
import time
from datetime import datetime, timedelta


log_dir = 'message_logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


def log_message(sender, message, recipient):
    """Enregistre le message dans un fichier nommé d'après l'expéditeur"""
    try:
        sender_filename = os.path.join(log_dir, f"{sender}_messages.txt")
        recipient_filename = os.path.join(log_dir, f"{recipient}_messages.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - From: {sender} To: {recipient} - {message}\n"

        # Enregistrer dans le fichier de l'expéditeur
        with open(sender_filename, 'a') as sender_file:
            sender_file.write(log_entry)

        # Enregistrer dans le fichier du réceptionner
        with open(recipient_filename, 'a') as recipient_file:
            recipient_file.write(log_entry)
    except Exception as e:
        print(f"Erreur lors de la journalisation du message : {e}")


def delete_old_logs():
    """Suppression ancien fichier journal après 8 heures"""
    while True:
        try:
            now = datetime.now()
            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if now - file_creation_time > timedelta(hours=8):
                    os.remove(filepath)
                    print(f"Fichier journal ancien supprimé : {filepath}")
        except Exception as e:
            print(f"Erreur lors de la suppression des anciens journaux : {e}")
        time.sleep(3600)


# Démarrer le thread qui nettoie les anciens fichiers journaux
threading.Thread(target=delete_old_logs, daemon=True).start()
