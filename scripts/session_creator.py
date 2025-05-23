import os
import json
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
SESSION_DIR = os.path.join(BASE, 'config')
BLACKLIST_PATH = os.path.join(BASE, 'blacklist.json')
os.makedirs(SESSION_DIR, exist_ok=True)

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load_session(username):
    path = os.path.join(SESSION_DIR, f"{username}.session")
    if os.path.exists(path):
        return load_json(path)
    return None

def save_session(username, api):
    session_path = os.path.join(SESSION_DIR, f"{username}.session")
    session_data = {
        "config": api.auth.settings["config"]
        "uuids": api.auth.settings["uuids"]
        "device_setting": api.auth.settings["device_settings"]
        "device_id": api.auth_settings["device_id"],
        "uuid": api.auth_settings["uuid"],
        "phone_id": api.auth_settings["phone_id"]
    }
    save_json(session_path, session_data)
    print(f"{Y}[•] Session sauvegardée : {session_path}{W}")

def get_instagram_session(data):
    username = data.get("username")
    password = data.get("password")
    uuids = data.get("uuids")
    device_settings = data.get("device_settings")
    config = data.get("config")
    last_login = data.get("last_login")
    user_agent = data.get("user_agent")

    if not all([username, password, device_settings]):
        print(f"{R}[!] Données incomplètes pour le compte : {username}{W}")
        return None

    # 1. Reconnexion via session existante
    saved_session = load_session(username)
    if saved_session:
        try:
            print(f"{C}[•] Tentative de reconnexion via session pour @{username}...{W}")
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
            print(f"{G}[✓] Reconnexion réussie via session : @{username}{W}")
            return api
        except Exception as e:
            print(f"{R}[✗] Session invalide ou expirée pour @{username} : {e}{W}")
            # On retente la connexion classique ci-dessous

    # 2. Connexion normale
    try:
        print(f"{C}[•] Connexion classique en cours pour @{username}...{W}")
        api = Client(
            username, password,
            config=auth["config"],
            uuids=ids_auth["uuids"],
            device_settings=setting_auth["device_settings"],
            user_agent=agent_auth["user_agent"],
            device_id=auth["device_id"],
            guid=auth["uuid"],
            phone_id=auth["phone_id"]
        )
        api.current_user()
        print(f"{G}[✓] Connexion réussie : @{username}{W}")
        save_session(username, api)
        return api

    except (ClientLoginError, ClientError) as e:
        print(f"{R}[✗] Erreur de connexion pour @{username} : {e}{W}")
        return None

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

if __name__ == "__main__":
    print(f"{C}--- Création/Reconnexion de sessions Instagram ---{W}")
    comptes, blacklist = get_all_accounts()

    if not comptes:
        print(f"{R}[!] Aucun compte valide trouvé dans config/.{W}")
        exit()

    for compte in comptes:
        username = compte.get("username")
        print(f"{C}>>> Traitement de : @{username}{W}")
        api = get_instagram_session(compte)
        if not api:
            if username not in blacklist:
                blacklist.append(username)
                print(f"{R}Ajout de @{username} à la blacklist.{W}")
                save_json(BLACKLIST_PATH, sorted(set(blacklist)))

    print(f"{Y}--- Terminé. Sessions prêtes pour les comptes valides.{W}")
