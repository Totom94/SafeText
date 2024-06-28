import os
import logging
from flask import Flask, redirect, url_for, session, abort, jsonify
from authlib.integrations.flask_client import OAuth
from logger import setup_logging

# Initialisation du logger
setup_logging()
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


# Liste des adresses e-mail Google autorisées → à paramétrer // Protection supplémentaire
AUTHORIZED_EMAILS = {'safetextotp@gmail.com'}


def get_authorized_emails():
    """Récupération des adresses e-mail Google autorisées depuis la base de données"""
    return AUTHORIZED_EMAILS


@app.route('/')
def index():
    """Page d'accueil"""
    return '''
            <h1>Bienvenue sur l'application OAuth</h1>
            <a href="/login">Connectez-vous avec Google</a>
        '''


@app.route('/login')
def login():
    """Redirection vers l'URL d'autorisation"""
    try:
        redirect_uri = url_for('authorize', _external=True)
        logger.info(f"URI de redirection: {redirect_uri}")
        print(f"URI de redirection: {redirect_uri}")
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error(f"Erreur lors de la redirection d'authentification : {str(e)}")
        return jsonify(error=str(e)), 500


@app.route('/logout')
def logout():
    """Suppression des informations utilisateur de la session"""
    session.pop('user', None)
    logger.info("Utilisateur déconnecté.")
    return redirect(url_for('index'))


@app.route('/callback')
def authorize():
    """Récupération du jeton d'accès et des informations utilisateur"""
    try:
        token = google.authorize_access_token()
        userinfo_resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        userinfo = userinfo_resp.json()
        user_email = userinfo['email']

        logger.info(f"Utilisateur connecté avec l'email : {user_email}")

        # Vérification de l'adresse e-mail
        if user_email not in AUTHORIZED_EMAILS:
            logger.warning(f"Accès refusé pour l'email : {user_email}")
            return abort(403)  # Accès refusé

        # Stockage des informations utilisateur dans la session
        session['user'] = userinfo

        # Écrire l'état d'authentification dans un fichier
        with open('auth_status.txt', 'w') as f:
            f.write(user_email)
            logger.info("État d'authentification enregistré.")

        return redirect(url_for('chat'))  # Redirection vers la page de chat après une connexion réussie
    except Exception as e:
        logger.error(f"Erreur lors de l'autorisation : {str(e)}")
        return jsonify(error=str(e)), 500


@app.route('/chat')
def chat():
    """Vérification de l'état d'authentification"""
    if 'user' not in session:
        logger.info("Tentative d'accès non autorisé à la page de chat.")
        return redirect(url_for('login'))
    logger.info(f"Accès à la page de chat par l'utilisateur : {session['user']['email']}")
    return '''
            <h1>Bienvenue sur l'application de chat</h1>
            <p>Connecté en tant que : {}</p>
            <a href="/logout">Déconnexion</a>
        '''.format(session['user']['email'])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
