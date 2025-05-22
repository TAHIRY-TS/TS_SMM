import os
import json
import time
import datetime
import random
from instagram_private_api import Client, ClientError

# Dossiers
CONFIG_DIR = "scripts/config"
SESSION_DIR = "sessions"
LOG_FILE = "logs.txt"

# Couleurs ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
LIGHT_RED = "\033[91m"
RESET = "\033[0m"

os.makedirs(SESSION_DIR, exist_ok=True)

def timestamp():
    return f"{GREEN}[TS {datetime.datetime.now().strftime('%H:%M:%S')}] {RESET}"

def log(message, level="info"):
    colors = {
        "info": YELLOW,
        "success": GREEN,
        "error": RED,
        "fatal": LIGHT_RED
    }
    color = colors.get(level, RESET)
    final = f"{timestamp()}{color}{message}{RESET}"
    with open(LOG_FILE, "a") as f:
        f.write(final + "\n")
    print(final)

def load_profiles():
    profiles = []
    files = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]
    random.shuffle(files)
    for file in files:
        path = os.path.join(CONFIG_DIR, file)
        try:
            with open(path, "r") as f:
                data = json.load(f)
                data["__file__"] = file
                profiles.append(data)
        except Exception as e:
            log(f"[!] Erreur lecture {file}: {e}", level="fatal")
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
        log(f"[...] Test de session existante pour {username}", level="info")
        api = Client(username, None, settings=session_settings)
        api.current_user()
        log(f"[✓] Session valide : {username}", level="success")
        return api
    except Exception as e:
        log(f"[X] Session invalide : {username} → suppression", level="error")
        os.remove(path)
        return None

def login_and_create_session(profile):
    username = profile.get("username")
    password = profile.get("password")
    uuids = profile.get("uuids", {})
    device = profile.get("device_settings", {})
    user_agent = profile.get("user_agent", "")
    config = profile.get("config", {})
    cookies = profile.get("cookies", {})
    authorization = config.get("authorization_data", {})

    if not username or not password:
        log(f"[!] Profil invalide ({profile.get('__file__', 'inconnu')}) : username ou password manquant", level="fatal")
        return None

    settings = {
        "uuid": uuids.get("uuid"),
        "phone_id": uuids.get("phone_id"),
        "client_session_id": uuids.get("client_session_id"),
        "advertising_id": uuids.get("advertising_id"),
        "android_device_id": uuids.get("android_device_id"),
        "device_settings": device,
        "user_agent": user_agent,
        "cookies": cookies,
        "last_login": profile.get("last_login"),
        "config": {
            "authorization_data": authorization,
            "mid": config.get("mid"),
            "ig_u_rur": config.get("ig_u_rur"),
            "ig_www_claim": config.get("ig_www_claim"),
        }
    }

    log(f"[+] Tentative de reconnexion avec paramètres enregistrés : {username}", level="info")
    try:
        api = Client(username, password, settings=settings)
        with open(session_file_path(username), "w") as f:
            json.dump(api.settings, f)
        log(f"[✓] Connexion réussie & session sauvegardée : {username}", level="success")
        return api
    except ClientError as e:
        log(f"[X] Erreur de connexion : {username} → {e}", level="error")
    except Exception as e:
        log(f"[!] Erreur inattendue : {username} → {e}", level="fatal")
    return None

def main():
    log("=== Démarrage : Création de sessions Instagram ===", level="info")
    profiles = load_profiles()
    for profile in profiles:
        username = profile.get("username", "inconnu")
        log(f"\n=== Traitement : {username} ===", level="info")
        api = use_existing_session(username)
        if not api:
            api = login_and_create_session(profile)
        time.sleep(2)
    log("=== Fin du traitement des comptes ===\n", level="info")

if __name__ == "__main__":
    main()
