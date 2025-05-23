import os
import json
import random
import time
from instagram_private_api import Client, ClientError

# Couleurs terminal
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[96m'
W = '\033[0m'

# Dossiers
BASE = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE, 'config')

def get_profiles():
    return [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]

def load_profile(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    if os.path.getsize(path) == 0:
        raise ValueError(f"Fichier vide : {path}")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur de lecture JSON dans {path} : {e}")

def save_session(path, settings):
    with open(path, 'w') as f:
        json.dump(settings, f)

def try_login(data, session_file):
    try:
        device = data.get('device_settings', {})
        uuids = data.get('uuids', {})
        username = data.get('username')
        password = data.get('password')
        user_agent = sanitize_user_agent(data.get('user_agent', ''))

        api = Client(
            username, password,
            device_id=uuids.get('android_device_id'),
            guid=uuids.get('uuid'),
            phone_id=uuids.get('phone_id'),
            user_agent=user_agent,
            device=device
        )
        save_session(session_file, api.settings)
        print(f"{G}[✓] Connexion réussie : {username}{W}")
        return api
    except ClientError as e:
        print(f"{R}[✗] Erreur de connexion : {e}{W}")
        return None
    except Exception as e:
        print(f"{R}[✗] Erreur inattendue : {e}{W}")
        return None

def process_profile(profile):
    json_path = os.path.join(CONFIG_DIR, profile)
    session_path = json_path.replace('.json', '.session')

    try:
        data = load_profile(json_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"{R}[✗] {e}{W}")
        return

    username = data['username']
    print(f"{Y}[*] Traitement du profil : {username}{W}")
    time.sleep(4)

    if os.path.exists(session_path):
        try:
            with open(session_path, 'r') as f:
                session = json.load(f)
            api = Client(username, data['password'], settings=session)
            api.current_user()
            print(f"{C}[•] Session valide : {username}{W}")
            return
        except Exception:
            print(f"{Y}[!] Session expirée ou corrompue : {username}{W}")
            os.remove(session_path)

    print(f"{B}[*] Reconnexion à {username}...{W}")
    api = try_login(data, session_path)
    if api:
        me = api.current_user()
        print(f"{G}[✓] Utilisateur connecté : @{me['user']['username']}{W}")
        time.sleep(2)

if __name__ == '__main__':
    print(f"{C}--- Traitement aléatoire de tous les profils ---{W}")
    profiles = get_profiles()
    random.shuffle(profiles)

    for profile in profiles:
        process_profile(profile)

    print(f"{G}\n[✓] Tous les profils ont été traités.{W}")
