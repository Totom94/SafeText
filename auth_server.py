import os
from flask import Flask, redirect, url_for, session, abort
from authlib.integrations.flask_client import OAuth


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
    return AUTHORIZED_EMAILS


@app.route('/')
def index():
    return '''
            <h1>Welcome to the OAuth App</h1>
            <a href="/login">Login with Google</a>
        '''


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    print(f"Redirect URI: {redirect_uri}")  # Affiche l'URL de redirection pour débogage
    return google.authorize_redirect(redirect_uri)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/callback')
def authorize():
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


@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('login'))
    return '''
            <h1>Welcome to the Chat App</h1>
            <p>Logged in as: {}</p>
            <a href="/logout">Logout</a>
        '''.format(session['user']['email'])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
