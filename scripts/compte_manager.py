import os
import json
import uuid
import time
from getpass import getpass
from datetime import datetime
from instagram_private_api import Client, ClientCompatPatch, ClientError

CONFIG_DIR = 'config'
SESSIONS_DIR = 'sessions'
LOG_FILE = 'history.log'

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

def log_event(event):
    with open(LOG_FILE, 'a') as log:
        log.write(f"[TS {datetime.now().strftime('%H:%M:%S')}] {event}\n")

def get_device_info():
    props = {}
    try:
        props['manufacturer'] = os.popen('getprop ro.product.manufacturer').read().strip()
        props['model'] = os.popen('getprop ro.product.model').read().strip()
        props['android_version'] = os.popen('getprop ro.build.version.release').read().strip()
        props['dpi'] = os.popen('wm density').read().split(":")[-1].strip()
        resolution = os.popen("wm size").read().split(":")[-1].strip()
        props['resolution'] = resolution if resolution else "1080x1920"
    except Exception:
        props = {
            "manufacturer": "Xiaomi",
            "model": "Redmi Note 7 Pro",
            "android_version": "10",
            "dpi": "440",
            "resolution": "1080x2340"
        }
    return props

def create_profile(username, password):
    device_info = get_device_info()
    profile = {
        "username": username,
        "password": password,
        "uuid": str(uuid.uuid4()),
        "phone_id": str(uuid.uuid4()),
        "device_id": f"android-{uuid.uuid4().hex[:16]}",
        "device": device_info
    }
    config_path = os.path.join(CONFIG_DIR, f"{username}.json")
    with open(config_path, 'w') as f:
        json.dump(profile, f, indent=4)
    print(f"[✓] Profil créé : {config_path}")
    log_event(f"[+] Profil créé pour {username}")
    return profile

def load_profile(username):
    config_path = os.path.join(CONFIG_DIR, f"{username}.json")
    if not os.path.isfile(config_path):
        print("[!] Profil introuvable.")
        return None
    with open(config_path) as f:
        return json.load(f)

def save_session(api, username):
    path = os.path.join(SESSIONS_DIR, f"{username}_session.session")
    with open(path, 'w') as f:
        json.dump(api.settings, f)
    print(f"[✓] Session sauvegardée : {path}")
    log_event(f"[+] Session sauvegardée pour {username}")

def login(username):
    profile = load_profile(username)
    if not profile:
        return
    session_path = os.path.join(SESSIONS_DIR, f"{username}_session.session")

    try:
        if os.path.exists(session_path):
            with open(session_path) as f:
                settings = json.load(f)
            print(f"[+] Tentative de reconnexion avec paramètres enregistrés : {username}")
            api = Client(profile['username'], profile['password'], settings=settings)
        else:
            print(f"[+] Connexion initiale pour {username}...")
            api = Client(
                profile['username'],
                profile['password'],
                uuid=profile['uuid'],
                phone_id=profile['phone_id'],
                device_id=profile['device_id']
            )
            save_session(api, username)
        print(f"[✓] Connexion réussie : @{api.authenticated_user_name}")
        log_event(f"[✓] Connexion réussie : @{username}")
    except ClientError as e:
        print(f"[X] Erreur de connexion : {username} → {e}")
        log_event(f"[X] Erreur de connexion : {username} → {e}")
    except Exception as e:
        print(f"[!] Exception inattendue : {e}")
        log_event(f"[!] Exception inattendue : {username} → {e}")

def list_profiles():
    files = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    if not files:
        print("Aucun profil trouvé.")
    else:
        for i, f in enumerate(files, 1):
            print(f"{i}. {f.replace('.json','')}")

def delete_profile(username):
    config_file = os.path.join(CONFIG_DIR, f"{username}.json")
    session_file = os.path.join(SESSIONS_DIR, f"{username}_session.session")
    if os.path.exists(config_file):
        os.remove(config_file)
    if os.path.exists(session_file):
        os.remove(session_file)
    print(f"[✓] {username} supprimé.")
    log_event(f"[-] Profil supprimé : {username}")

def menu():
    while True:
        print("\n--- MENU GESTION DE COMPTES IG ---")
        print("1. Ajouter un compte")
        print("2. Tester une session")
        print("3. Supprimer un compte")
        print("4. Lister les comptes")
        print("0. Quitter")

        choix = input("Choix : ")
        if choix == '1':
            username = input("Nom d'utilisateur : ").strip()
            password = getpass("Mot de passe : ")
            create_profile(username, password)
        elif choix == '2':
            username = input("Nom d'utilisateur : ").strip()
            login(username)
        elif choix == '3':
            username = input("Nom d'utilisateur à supprimer : ").strip()
            delete_profile(username)
        elif choix == '4':
            list_profiles()
        elif choix == '0':
            break
        else:
            print("[!] Choix invalide.")

if __name__ == '__main__':
    menu()
