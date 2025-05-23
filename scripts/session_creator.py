import os
import json
import random
from instagram_private_api import Client, ClientError, ClientLoginError

# Couleurs
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'

BASE = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE, 'config')
SESSION_DIR = os.path.join(BASE, 'sessions')
BLACKLIST_PATH = os.path.join(CONFIG_DIR, 'blacklist.json')
os.makedirs(SESSION_DIR, exist_ok=True)

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def get_instagram_api(data):
    username = data["username"]
    session_path = os.path.join(SESSION_DIR, f"ig_{username}.session")

    try:
        if os.path.exists(session_path):
            session_data = load_json(session_path)
            api = Client(
                username,
                data["password"],
                user_agent=data["user_agent"],
                device_id=session_data["device_id"],
                guid=session_data["uuid"],
                phone_id=session_data["phone_id"]
            )
            print(f"{G}[✓] Session restaurée depuis .session pour @{username}{W}")
        else:
            auth = data["authorization_data"]
            api = Client(
                username,
                data["password"],
                user_agent=data["user_agent"],
                device_id=auth["device_id"],
                guid=auth["uuid"],
                phone_id=auth["phone_id"]
            )
            session_auth = {
                "device_id": api.auth_settings["device_id"],
                "uuid": api.auth_settings["uuid"],
                "phone_id": api.auth_settings["phone_id"]
            }
            save_json(session_path, session_auth)
            print(f"{Y}[•] Session Instagram sauvegardée dans {session_path}{W}")

        # Vérification
        api.current_user()
        return api

    except (ClientError, ClientLoginError) as e:
        print(f"{R}[✗] Connexion échouée pour @{username} : {e}{W}")
        return None

def lister_comptes_valides():
    blacklist = load_json(BLACKLIST_PATH)
    fichiers = [f for f in os.listdir(CONFIG_DIR) if f.startswith("user_") and f.endswith(".json")]
    comptes = []
    for f in fichiers:
        data = load_json(os.path.join(CONFIG_DIR, f))
        username = data.get("username")
        if username and username not in blacklist:
            comptes.append(os.path.join(CONFIG_DIR, f))
    return comptes

if __name__ == '__main__':
    print(f"{C}--- Connexion Instagram via fichiers .session ---{W}")
    comptes = lister_comptes_valides()
    if not comptes:
        print(f"{R}[!] Aucun compte valide trouvé.{W}")
        exit()

    blacklist = load_json(BLACKLIST_PATH)
    success = 0
    failed = 0

    for chemin in comptes:
        data = load_json(chemin)
        username = data["username"]
        print(f"{C}--- Tentative pour @{username} ---{W}")
        api = get_instagram_api(data)
        if api:
            success += 1
            print(f"{G}[✓] Succès : @{username}{W}")
        else:
            failed += 1
            blacklist.append(username)
            save_json(BLACKLIST_PATH, list(set(blacklist)))

    print(f"\n{Y}--- Résumé ---{W}")
    print(f"{G}Comptes réussis : {success}{W}")
    print(f"{R}Comptes échoués : {failed}{W}")
    print(f"{C}Liste noire mise à jour dans blacklist.json{W}")
