import pyotp
import qrcode


def generate_otp_secret():
    return pyotp.random_base32()


def generate_totp_uri(secret, name, issuer_name):
    try:
        return pyotp.totp.TOTP(secret).provisioning_uri(name=name, issuer_name=issuer_name)
    except Exception as e:
        print(f"Erreur lors de la génération de l'URI TOTP : {e}")
        raise  # Re-lève l'exception pour une gestion ultérieure si nécessaire


def create_qr_code(uri, file_path):
    try:
        qr = qrcode.make(uri)
        qr.save(file_path)
        print(f"QR Code créé avec succès : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la création du code QR : {e}")
        raise  # Re-lève l'exception pour une gestion ultérieure si nécessaire


def verify_totp(secret, otp):
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(otp)
    except Exception as e:
        print(f"Erreur lors de la vérification TOTP : {e}")
        return False  # Retourne False ou gère d'autres manières en fonction du besoin


if __name__ == "__main__":
    try:
        otp_secret = generate_otp_secret()
        username = "user1"
        issuer_name = "SafeText"
        totp_uri = generate_totp_uri(otp_secret, username, issuer_name)

        qr_path = f"{username}_qrcode.png"
        create_qr_code(totp_uri, qr_path)

        print(f"Secret OTP généré : {otp_secret}")
        print(f"URI TOTP généré : {totp_uri}")
        print(f"QR Code sauvegardé : {qr_path}")

        # Exemple de vérification TOTP
        otp_input = input("Entrez le code OTP : ")
        if verify_totp(otp_secret, otp_input):
            print("Code OTP valide.")
        else:
            print("Code OTP invalide.")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
