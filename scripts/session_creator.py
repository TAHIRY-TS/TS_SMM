import os
import json
import time
from instagram_private_api import Client, ClientError

CONFIG_DIR = "config"
SESSION_DIR = "sessions"
LOG_FILE = "logs.txt"

os.makedirs(SESSION_DIR, exist_ok=True)

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")
    print(message)

def load_profiles():
    profiles = []
    for file in os.listdir(CONFIG_DIR):
        if file.endswith(".json"):
            path = os.path.join(CONFIG_DIR, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    data["__file__"] = file  # pour afficher en cas d'erreur
                    profiles.append(data)
            except Exception as e:
                log(f"[!] Erreur lecture {file}: {e}")
    return profiles

def session_file_path(username):
    return os.path.join(SESSION_DIR, f"{username}_session.json")

def use_existing_session(username):
    path = session_file_path(username)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            session_settings = json.load(f)
        log(f"[...] Test de session existante pour {username}")
        api = Client(username, None, settings=session_settings)
        api.current_user()
        log(f"[✓] Session valide : {username}")
        return api
    except Exception as e:
        log(f"[X] Session invalide : {username} → suppression")
        os.remove(path)
        return None

def login_and_create_session(profile):
    username = profile.get("username")
    password = profile.get("password")
    uuids = profile.get("uuids", {})
    device = profile.get("device_settings", {})
    user_agent = profile.get("user_agent", "")

    if not username or not password:
        log(f"[!] Profil invalide ({profile.get('__file__', 'inconnu')}) : username ou password manquant")
        return None

    settings = {
        "uuid": uuids.get("uuid"),
        "phone_id": uuids.get("phone_id"),
        "client_session_id": uuids.get("client_session_id"),
        "advertising_id": uuids.get("advertising_id"),
        "android_device_id": uuids.get("android_device_id"),
        "device_settings": device,
        "user_agent": user_agent
    }

    log(f"[+] Tentative de connexion : {username}")
    try:
        api = Client(username, password, settings=settings)
        with open(session_file_path(username), "w") as f:
            json.dump(api.settings, f)
        log(f"[✓] Connexion réussie & session sauvegardée : {username}")
        return api
    except ClientError as e:
        log(f"[X] Erreur de connexion : {username} → {e}")
    except Exception as e:
        log(f"[!] Erreur inattendue : {username} → {e}")
    return None

def main():
    log("=== Lancement de la génération de sessions ===")
    profiles = load_profiles()
    for profile in profiles:
        username = profile.get("username", "inconnu")
        log(f"\n=== Traitement : {username} ===")
        api = use_existing_session(username)
        if not api:
            api = login_and_create_session(profile)
        time.sleep(3)
    log("=== Fin du script ===\n")

if __name__ == "__main__":
    main()
