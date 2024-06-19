import pyotp
import qrcode


def generate_otp_secret():
    return pyotp.random_base32()


def generate_totp_uri(secret, name, issuer_name):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=name, issuer_name=issuer_name)


def create_qr_code(uri, file_path):
    qr = qrcode.make(uri)
    qr.save(file_path)


def verify_totp(secret, otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)
