import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging():
    # Création du dossier de logs s'il n'existe pas
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configuration du format de journalisation
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Supprimer tous les handlers existants du logger racine
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configuration du logger racine
    logging.basicConfig(level=logging.INFO, format=log_format)

    # Configuration du handler pour écrire dans un fichier avec rotation
    handler = RotatingFileHandler(
        f"{log_dir}/chatbox.log",
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5
    )
    handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(handler)

    logging.info("Configuration de journalisation établie.")


# Appel de la fonction de configuration lors de l'import du module
setup_logging()
