import os
from flask import Flask, redirect, url_for, session, abort, jsonify
from authlib.integrations.flask_client import OAuth


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
        print(f"URI de redirection: {redirect_uri}")
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/logout')
def logout():
    """Suppression des informations utilisateur de la session"""
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/callback')
def authorize():
    """Récupération du jeton d'accès et des informations utilisateur"""
    try:
        token = google.authorize_access_token()
        userinfo_resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        userinfo = userinfo_resp.json()
        user_email = userinfo['email']

        # Vérification de l'adresse e-mail
        if user_email not in AUTHORIZED_EMAILS:
            return abort(403)  # Accès refusé

        # Stockage des informations utilisateur dans la session
        session['user'] = userinfo

        # Écrire l'état d'authentification dans un fichier
        with open('auth_status.txt', 'w') as f:
            f.write(user_email)

        return redirect(url_for('chat'))  # Redirection vers la page de chat après une connexion réussie
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/chat')
def chat():
    """Vérification de l'état d'authentification"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return '''
            <h1>Bienvenue sur l'application de chat</h1>
            <p>Connecté en tant que : {}</p>
            <a href="/logout">Déconnexion</a>
        '''.format(session['user']['email'])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
