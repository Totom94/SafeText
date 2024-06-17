# SafeText - Application de Chat Sécurisée

SafeText est une application de chat sécurisée permettant aux utilisateurs de se connecter, de s'authentifier et de communiquer via des messages chiffrés. Ce projet utilise une architecture client-serveur avec une interface utilisateur graphique (GUI) basée sur Tkinter.

## Fonctionnalités

- Authentification des utilisateurs (inscription et connexion)
- Communication en temps réel entre les utilisateurs
- Liste des utilisateurs connectés et déconnectés
- Interface utilisateur graphique simple et intuitive
- Chiffrement des messages pour une communication sécurisée

## Prérequis

- Python 3.x
- Bibliothèques Python : `tkinter`, `socket`, `threading`, `sqlite3`

## Installation

1. Clonez le dépôt GitHub :
    ```bash
    git clone https://github.com/Totom94/SafeText.git
    cd SafeText
    ```

2. Créez un environnement virtuel et activez-le :
    ```bash
    python -m venv venv
    source venv/bin/activate   # Sur Windows, utilisez `venv\Scripts\activate`
    ```

3. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    pip install qrcode
    pip install pyotp
    ```

## Configuration

1. Créez les certificats SSL pour sécuriser la communication :
    ```bash
    openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365
    ```

2. Placez les fichiers `server.key` et `server.crt` dans le répertoire `ssl` de votre répertoire utilisateur.

3. Initialisez la base de données SQLite :
    ```bash
    python bdd.py
    ```

## Utilisation

1. Démarrez le serveur :
    ```bash
    python server.py
    ```

2. Lancez l'interface utilisateur :
    ```bash
    python interface.py
    ```

3. Connectez-vous ou inscrivez-vous avec un nouveau compte utilisateur.

4. Une fois connecté, utilisez la fenêtre de chat pour envoyer et recevoir des messages.

## Authentification à Deux Facteurs (AF2) avec Authy

Pour activer l'authentification à deux facteurs avec Authy :
- Installez Authy sur votre appareil mobile.
- Scannez le QR code généré par l'application avec Authy pour configurer l'AF2.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer, veuillez suivre les étapes ci-dessous :

1. Forkez le projet.
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nom-de-votre-fonctionnalite`).
3. Commitez vos modifications (`git commit -m 'Ajout de ma super fonctionnalité'`).
4. Poussez votre branche (`git push origin feature/nom-de-votre-fonctionnalite`).
5. Ouvrez une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.
