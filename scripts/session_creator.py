import os
import json
import random
from instagram_private_api import Client, ClientError, ClientLoginError

# Couleurs terminal
G = '\033[92m'  # Vert
R = '\033[91m'  # Rouge
Y = '\033[93m'  # Jaune
C = '\033[96m'  # Cyan
W = '\033[0m'   # Reset

# Dossiers
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

def get_instagram_session(data):
    username = data.get("username")
    password = data.get("password")
    auth = data.get("authorization_data", {})
    user_agent = data.get("user_agent", "Instagram 123.0.0.0")

    if not all([username, password, auth]):
        print(f"{R}[!] Données incomplètes pour le compte : {username}{W}")
        return None

    try:
        # Connexion
        api = Client(
            username, password,
            user_agent=user_agent,
            device_id=auth["device_id"],
            guid=auth["uuid"],
            phone_id=auth["phone_id"]
        )
        api.current_user()
        print(f"{G}[✓] Connexion réussie : @{username}{W}")

        # Sauvegarde session
        session_path = os.path.join(SESSION_DIR, f"ig_{username}.session")
        session_data = {
            "device_id": api.auth_settings["device_id"],
            "uuid": api.auth_settings["uuid"],
            "phone_id": api.auth_settings["phone_id"]
        }
        save_json(session_path, session_data)
        print(f"{Y}[•] Session sauvegardée : {session_path}{W}")
        return api

    except (ClientLoginError, ClientError) as e:
        print(f"{R}[✗] Erreur connexion @{username} : {e}{W}")
        return None

def get_all_accounts():
    blacklist = load_json(BLACKLIST_PATH)
    fichiers = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]
    comptes = []
    for f in fichiers:
        chemin = os.path.join(CONFIG_DIR, f)
        data = load_json(chemin)
        if data.get("username") not in blacklist:
            comptes.append(data)
    return comptes

if __name__ == "__main__":
    print(f"{C}--- Création de sessions Instagram depuis config/ ---{W}")
    comptes = get_all_accounts()
    blacklist = load_json(BLACKLIST_PATH)

    if not comptes:
        print(f"{R}[!] Aucun compte valide trouvé dans config/.{W}")
        exit()

    for compte in comptes:
        username = compte.get("username")
        print(f"{C}>>> Traitement de : @{username}{W}")
        api = get_instagram_session(compte)
        if not api:
            blacklist.append(username)
            print(f"{R}Ajout de @{username} à la blacklist.{W}")
            save_json(BLACKLIST_PATH, list(set(blacklist)))

    print(f"{Y}--- Terminé. Sessions créées pour comptes valides.{W}")
