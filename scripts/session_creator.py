import os
import json
from instagram_private_api import Client, ClientError, ClientLoginError
from urllib.parse import urlparse

# Couleurs terminal
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'

# Dossiers
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_DIR = os.path.join(BASE, 'scripts', 'config')
SESSION_DIR = CONFIG_DIR
BLACKLIST_PATH = os.path.join(BASE, 'blacklist.json')
SELECTED_USER_PATH = os.path.join(CONFIG_DIR, 'selected_user.json')

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
        "config": api.auth.settings.get("config"),
        "uuids": api.auth.settings.get("uuids"),
        "device_settings": api.auth.settings.get("device_settings"),
        "device_id": api.auth_settings.get("device_id"),
        "uuid": api.auth_settings.get("uuid"),
        "phone_id": api.auth_settings.get("phone_id"),
        "user_agent": api.auth_settings.get("user_agent")
    }
    save_json(session_path, session_data)
    print(f"{Y}[•] Session sauvegardée : {session_path}{W}")

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
        print(f"{R}[!] Données incomplètes pour le compte : {username}{W}")
        return None

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
            print(f"{G}[✓] Reconnexion réussie : @{username}{W}")
            return api
        except Exception as e:
            print(f"{R}[✗] Session expirée : {e}{W}")

    try:
        print(f"{C}[•] Connexion classique pour @{username}...{W}")
        api = Client(
            username, password,
            config=config,
            uuids=uuids,
            device_settings=device_settings,
            user_agent=user_agent,
            device_id=device_id,
            guid=guid,
            phone_id=phone_id,
            authenticate=False
        )

        api.pre_login_flow()
        api.login()
        api.post_login_flow()

        api.current_user()
        print(f"{G}[✓] Connexion réussie : @{username}{W}")
        save_session(username, api)
        return api

    except ClientLoginError as e:
        print(f"{R}[✗] Erreur de login @{username} : {e}{W}")
    except ClientError as e:
        if 'challenge_required' in str(e).lower():
            print(f"{R}[!] Vérification requise pour @{username} (challenge_required).{W}")
        elif 'checkpoint_required' in str(e).lower():
            print(f"{R}[!] Checkpoint Instagram requis pour @{username}.{W}")
        elif e.code == 403:
            print(f"{R}[!] Erreur 403 (interdit). Blocage possible pour @{username}.{W}")
        elif e.code == 400:
            print(f"{R}[!] Erreur 400 (mauvaise requête). @{username} peut être mal configuré.{W}")
        else:
            print(f"{R}[✗] Erreur API : {e}{W}")
    except Exception as e:
        print(f"{R}[✗] Erreur inconnue @{username} : {e}{W}")
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

def extraire_user_id_depuis_lien(api, lien):
    try:
        path = urlparse(lien).path.strip('/')
        username = path.split('/')[0]
        user_info = api.username_info(username)
        return user_info['user']['pk']
    except Exception as e:
        print(f"{R}[!] Impossible d'extraire l'ID depuis {lien} : {e}{W}")
        return None

def effectuer_suivi(api, user_id):
    try:
        api.friendships_create(user_id)
        print(f"{G}[✓] Action FOLLOW réussie pour ID {user_id}{W}")
    except Exception as e:
        print(f"{R}[✗] Erreur lors du FOLLOW : {e}{W}")

if __name__ == "__main__":
    print(f"{C}--- Création/Reconnexion de sessions Instagram ---{W}")
    comptes, blacklist = get_all_accounts()

    if not comptes:
        print(f"{R}[!] Aucun compte valide trouvé dans config/.{W}")
        exit()

    lien = input(f"{Y}Entrez le lien du profil à suivre : {W}").strip()
    if not lien:
        print(f"{R}[!] Aucun lien fourni. Opération annulée.{W}")
        exit()

    for compte in comptes:
        username = compte.get("username")
        print(f"{C}>>> Traitement de : @{username}{W}")
        api = get_instagram_session(compte)
        if not api:
            if username not in blacklist:
                blacklist.append(username)
                save_json(BLACKLIST_PATH, sorted(set(blacklist)))
            continue

        user_id = extraire_user_id_depuis_lien(api, lien)
        if user_id:
            effectuer_suivi(api, user_id)
            save_json(SELECTED_USER_PATH, compte)
            break  # Utiliser un seul compte

    print(f"{Y}--- Fin de traitement.{W}")
