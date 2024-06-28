from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os


def generate_rsa_keys(private_key_path, public_key_path):
    """Génère les clés RSA (privée et publique) et les sauvegarde dans les fichiers spécifiés."""
    try:
        # Vérifier si les fichiers de clés existent déjà
        if os.path.exists(private_key_path) or os.path.exists(public_key_path):
            print("Les clés RSA existent déjà.")
            return

        # Générer la clé privée RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Obtenir la clé publique à partir de la clé privée
        public_key = private_key.public_key()

        # Sauvegarder la clé privée au format PEM
        with open(private_key_path, "wb") as priv_file:
            priv_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
            print(f"Clé privée RSA générée avec succès : {private_key_path}")

        # Sauvegarder la clé publique au format PEM
        with open(public_key_path, "wb") as pub_file:
            pub_file.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
            print(f"Clé publique RSA générée avec succès : {public_key_path}")
    except Exception as e:
        print(f"Erreur lors de la génération des clés RSA : {e}")
        raise


if __name__ == "__main__":
    try:
        private_key_path = "C:\\Users\\tomgo\\ssl\\private_key.pem"
        public_key_path = "C:\\Users\\tomgo\\ssl\\public_key.pem"
        generate_rsa_keys(private_key_path, public_key_path)
    except Exception as e:
        print(f"Une erreur est survenue : {e}")



