import logging
import time
from logging.handlers import RotatingFileHandler
import os
import threading
from datetime import datetime, timedelta

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def setup_logging():
    # Configuration du format de journalisation
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Supprimer tous les handlers existants du logger racine
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configuration du logger racine
    logging.basicConfig(level=logging.INFO, format=log_format)

    # Générer un nom de fichier unique avec timestamp
    log_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_chatbox.log"

    # Configuration du handler pour écrire dans un fichier avec rotation
    handler = RotatingFileHandler(
        os.path.join(log_dir, log_filename),
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5  # Garder les 5 derniers fichiers de logs
    )
    handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(handler)

    logging.info("Configuration de journalisation établie.")

def delete_old_logs(days=7):
    """
    Supprime les fichiers de logs plus anciens que le nombre de jours spécifié.
    """
    while True:
        now = datetime.now()
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if os.path.isfile(filepath):
                file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if now - file_creation_time > timedelta(days=days):
                    os.remove(filepath)
                    logging.info(f"Deleted old log file: {filepath}")
        # Vérification chaque jour
        time.sleep(86400)


# Démarrage du thread pour supprimer les anciens logs
threading.Thread(target=delete_old_logs, daemon=True).start()

# Configuration de la journalisation au démarrage de l'application
setup_logging()
