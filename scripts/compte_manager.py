import os import sys import json import uuid import time import platform import subprocess from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(file)) ACCOUNTS_DIR = os.path.join(BASE_DIR, "accounts") CONFIG_DIR = os.path.join(BASE_DIR, "config") HISTORY_PATH = os.path.join(ACCOUNTS_DIR, "history.log")

os.makedirs(ACCOUNTS_DIR, exist_ok=True) os.makedirs(CONFIG_DIR, exist_ok=True)

def horloge(): return datetime.now().strftime("[TS %H:%M:%S]")

def info(msg): print(f"{horloge()} \033[1;34m{msg}\033[0m")

def success(msg): print(f"{horloge()} \033[1;32m{msg}\033[0m")

def erreur(msg): print(f"{horloge()} \033[1;31m{msg}\033[0m")

def enregistrer_historique(msg): with open(HISTORY_PATH, "a") as f: f.write(f"{horloge()} {msg}\n")

def get_uuid(): return str(uuid.uuid4())

def get_system_property(prop): try: return subprocess.check_output(['getprop', prop]).decode().strip() except Exception: return "unknown"

def get_android_info(): return { "manufacturer": get_system_property("ro.product.manufacturer"), "model": get_system_property("ro.product.model"), "device": get_system_property("ro.product.device"), "android_version": int(get_system_property("ro.build.version.sdk") or 0), "android_release": get_system_property("ro.build.version.release"), "dpi": "420",  # Valeur par défaut "resolution": "1080x1920",  # Valeur par défaut "refresh_rate": "60.0", "cpu": get_system_property("ro.product.board"), "board": get_system_property("ro.product.board"), "bootloader": get_system_property("ro.bootloader"), "brand": get_system_property("ro.product.brand"), "product": get_system_property("ro.product.name"), "fingerprint": get_system_property("ro.build.fingerprint"), "radio_version": get_system_property("gsm.version.baseband"), "build_id": get_system_property("ro.build.id"), "build_tags": get_system_property("ro.build.tags"), "build_type": get_system_property("ro.build.type"), "country": get_system_property("persist.sys.country") or "FR", "country_code": 261, "locale": get_system_property("persist.sys.locale") or "fr_FR", "timezone_offset": time.timezone * -1 }

def creer_profil_json(username, password): file_path = os.path.join(CONFIG_DIR, f"{username}.json") if os.path.exists(file_path): erreur("Ce compte existe déjà.") return

device_info = get_android_info()

data = {
    "username": username,
    "password": password,
    "uuids": {
        "phone_id": get_uuid(),
        "uuid": get_uuid(),
        "client_session_id": get_uuid(),
        "advertising_id": get_uuid(),
        "android_device_id": f"android-{uuid.uuid4().hex[:16]}",
        "request_id": get_uuid(),
        "tray_session_id": get_uuid(),
        "mid": f"a{uuid.uuid4().hex[:13].upper()}",
        "ig_u_rur": None,
        "ig_www_claim": "0",
        "authorization_data": {
            "ds_user_id": str(uuid.uuid4().int)[:11],
            "sessionid": f"{uuid.uuid4().int % 99999999999}%3A{uuid.uuid4().hex}%3A8%3AAY{uuid.uuid4().hex}",
            "cookies": {}
        },
        "last_login": time.time(),
        "device_settings": {
            "user_agent": f"Instagram 269.0.0.18.75 Android ({device_info['android_version']}/{device_info['android_release']}; {device_info['dpi']}; {device_info['resolution']}; {device_info['manufacturer']}; {device_info['model']}; {device_info['device']}; {device_info['cpu']})",
            **device_info
        }
    }
}

with open(file_path, "w") as f:
    json.dump(data, f, indent=4)
enregistrer_historique(f"[+] Ajout du compte : {username}")
success(f"Profil {username} ajouté avec succès.")

def supprimer_compte(username): path = os.path.join(CONFIG_DIR, f"{username}.json") if os.path.exists(path): os.remove(path) enregistrer_historique(f"[-] Supprimé : {username}") success(f"Compte {username} supprimé.") else: erreur("Ce compte n'existe pas.")

def lister_comptes(): fichiers = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")] if not fichiers: info("Aucun compte trouvé.") return print("\n\033[1;36m╔═════════════════ COMPTES ENREGISTRÉS ═══════════════╗\033[0m") for i, fichier in enumerate(fichiers, 1): print(f"  {i}. {fichier.replace('.json', '')}") print("\033[1;36m╚════════════════════════════════════════════════════╝\033[0m\n")

def supprimer_tous(): fichiers = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")] for f in fichiers: os.remove(os.path.join(CONFIG_DIR, f)) enregistrer_historique("[!] Tous les comptes ont été supprimés.") success("Tous les comptes ont été supprimés.")

def menu(): while True: print("\n\033[1;36m[ MENU DE GESTION DES COMPTES INSTAGRAM ]\033[0m") print("1. Ajouter un compte") print("2. Supprimer un compte") print("3. Lister les comptes") print("4. Supprimer tous les comptes") print("5. Quitter") choix = input("\nChoix : ") if choix == "1": username = input("Nom d'utilisateur : ") password = input("Mot de passe : ") creer_profil_json(username, password) elif choix == "2": username = input("Nom du compte à supprimer : ") supprimer_compte(username) elif choix == "3": lister_comptes() elif choix == "4": supprimer_tous() elif choix == "5": break else: erreur("Choix invalide.")

if name == "main": if len(sys.argv) == 1: menu() else: action = sys.argv[1] if action == "add" and len(sys.argv) == 4: creer_profil_json(sys.argv[2], sys.argv[3]) elif action == "list": lister_comptes() elif action == "delete" and len(sys.argv) >= 3: supprimer_compte(sys.argv[2]) elif action == "purge": supprimer_tous() else: print("Usage :") print("  python3 compte_manager.py                (menu interactif)") print("  python3 compte_manager.py add USER PASS") print("  python3 compte_manager.py list") print("  python3 compte_manager.py delete USER") print("  python3 compte_manager.py purge")

