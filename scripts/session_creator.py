import os
import json
from datetime import datetime
from instagram_private_api import Client, ClientError, ClientLoginError

# Couleurs terminal
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'

# Dossiers
BASE = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE, 'config')
SESSION_DIR = CONFIG_DIR
BLACKLIST_PATH = os.path.join(BASE, 'blacklist.json')
os.makedirs(SESSION_DIR, exist_ok=True)

# Logger stylisé avec heure
def log(msg, color=W):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{now}] {msg}{W}")

# JSON utils
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# Charger une session existante
def load_session(username):
    path = os.path.join(SESSION_DIR, f"{username}.session")
    if os.path.exists(path):
        return load_json(path)
    return None

# Sauvegarder une session
def save_session(username, api):
    session_path = os.path.join(SESSION_DIR, f"{username}.session")
    session_data = {
        "config": api.auth.settings.get("config"),
        "uuids": api.auth.settings.get("uuids"),
        "device_settings": api.auth.settings.get("device_settings"),
        "device_id": api.auth.settings.get("device_id"),
        "uuid": api.auth.settings.get("uuid"),
        "phone_id": api.auth.settings.get("phone_id"),
        "user_agent": api.auth.settings.get("user_agent")
    }
    save_json(session_path, session_data)
    log(f"Session sauvegardée : {session_path}", Y)

# Connexion Instagram
def get_instagram_session(data):
    username = data.get("username")
    password = data.get("password")
    uuids = data.get("uuids")
    device_settings = data.get("device_settings")
    config = data.get("config")
    user_agent = data.get("user_agent")
    device_id = uuids.get("android_device_id", None)
    guid = uuids.get("uuid", None)
    phone_id = uuids.get("phone_id", None)

    if not all([username, password, device_settings, uuids]):
        log(f"Données incomplètes pour le compte : {username}", R)
        return None

    # Tentative de reconnexion via session
    saved_session = load_session(username)
    if saved_session:
        try:
            log(f"Tentative de reconnexion via session pour @{username}...", C)
            api = Client(
                username, password,
                config=saved_session["config"],
                uuids=saved_session["uuids"],
                device_settings=saved_session["device_settings"],
                user_agent=saved_session["user_agent"],
                device_id=saved_session["device_id"],
                guid=saved_session["uuid"],
                phone_id=saved_session["phone_id"]
            )
            api.current_user()
            log(f"Reconnexion réussie via session : @{username}", G)
            return api
        except Exception as e:
            log(f"Session invalide pour @{username} : {e}", R)

    # Connexion normale
    try:
        log(f"Connexion classique en cours pour @{username}...", C)
        api = Client(
            username, password,
            config=config,
            uuids=uuids,
            device_settings=device_settings,
            user_agent=user_agent,
            device_id=device_id,
            guid=guid,
            phone_id=phone_id
        )
        api.current_user()
        log(f"Connexion réussie : @{username}", G)
        save_session(username, api)
        return api
    except (ClientLoginError, ClientError) as e:
        log(f"Erreur de connexion pour @{username} : {e}", R)
        return None

# Obtenir tous les comptes sauf blacklist
def get_all_accounts():
    blacklist = load_json(BLACKLIST_PATH)
    if not isinstance(blacklist, list):
        blacklist = []

    fichiers = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json") and f != "blacklist.json"]
    comptes = []
    for f in fichiers:
        chemin = os.path.join(CONFIG_DIR, f)
        data = load_json(chemin)
        if data.get("username") and data.get("username") not in blacklist:
            comptes.append(data)
    return comptes, blacklist

# Main
if __name__ == "__main__":
    log("--- Création/Reconnexion de sessions Instagram ---", C)
    comptes, blacklist = get_all_accounts()

    if not comptes:
        log("Aucun compte valide trouvé dans config/.", R)
        exit()

    for compte in comptes:
        username = compte.get("username")
        log(f">>> Traitement de : @{username}", C)
        api = get_instagram_session(compte)
        if not api:
            if username not in blacklist:
                blacklist.append(username)
                log(f"Ajout de @{username} à la blacklist.", R)
                save_json(BLACKLIST_PATH, sorted(set(blacklist)))

    log("--- Terminé. Sessions prêtes pour les comptes valides. ---", Y)
