import os
import ssl
from pathlib import Path


def load_ssl_context():
    # Obtient le répertoire personnel de l'utilisateur actuel
    home_dir = Path.home()
    # Spécifie un sous-dossier dans le répertoire personnel où les fichiers SSL sont censés être stockés
    ssl_dir = home_dir / "ssl"

    key_path = ssl_dir / "server.key"
    cert_path = ssl_dir / "server.crt"

    if not key_path.exists() or not cert_path.exists():
        raise FileNotFoundError(f"Les fichiers SSL n'ont pas été trouvés dans {ssl_dir}")

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    return ssl_context


