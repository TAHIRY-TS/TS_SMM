#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
import uuid
import subprocess
import re
from datetime import datetime, timezone

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT_DIR = os.path.join(PROJECT_DIR, 'scripts')
CONFIG_DIR = os.path.join(SCRIPT_DIR, 'config')
SESSION_DIR = os.path.join(SCRIPT_DIR, 'sessions')
LOG_FILE = os.path.join(SCRIPT_DIR, 'history.log')
LOGO_PATH = os.path.join(PROJECT_DIR, 'assets/logo.sh')

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

def check_cmd(cmd):
    return shutil.which(cmd) is not None

def titre_section(titre):
    if os.path.exists(LOGO_PATH):
        subprocess.call(['bash', LOGO_PATH])
    else:
        print("\033[1;33m[AVERTISSEMENT]\033[0m Logo non trouvé.")

    titre_formate = f" {titre.upper()} "
    largeur = 50
    terminal_width = shutil.get_terminal_size().columns
    padding = max((terminal_width - largeur) // 2, 0)
    spaces = ' ' * padding

    print(f"\n{spaces}\033[1;35m╔{'═' * largeur}╗\033[0m")
    print(f"{spaces}\033[1;35m║{titre_formate.center(largeur)}║\033[0m")
    print(f"{spaces}\033[1;35m╚{'═' * largeur}╝\033[0m\n")

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def horloge():
    return datetime.now().strftime("[TS %H:%M:%S]")

def log_action(action, username):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{horloge()} {action.upper()} - {username}\n")

def success(msg):
    print(f"\033[1;32m{horloge()} [SUCCÈS]\033[0m {msg}")

def erreur(msg):
    print(f"\033[1;31m{horloge()} [ERREUR]\033[0m {msg}")

def info(msg):
    print(f"\033[1;34m{horloge()} [INFO]\033[0m {msg}")

def safe_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        return ''

def get_prop(prop):
    if not check_cmd('getprop'):
        return ''
    try:
        return subprocess.check_output(['getprop', prop], encoding='utf-8').strip()
    except Exception:
        return None

def get_android_device_info():
    screen_size = '1080x1920'
    density = '420'
    if check_cmd('wm'):
        try:
            screen_size = subprocess.check_output(['wm', 'size'], encoding='utf-8').strip().split()[-1]
        except Exception:
            pass

    if check_cmd('dumpsys'):
        try:
            dpi_output = subprocess.check_output(['dumpsys', 'display'], encoding='utf-8')
            match = re.search(r'Physical density: (\d+)', dpi_output)
            density = match.group(1) if match else '420'
        except Exception:
            pass

    timezone_offset = int(datetime.now(timezone.utc).astimezone().utcoffset().total_seconds())

    uuids = {
        "phone_id": str(uuid.uuid4()),
        "uuid": str(uuid.uuid4()),
        "client_session_id": str(uuid.uuid4()),
        "advertising_id": str(uuid.uuid4()),
        "android_device_id": "android-" + uuid.uuid4().hex[:16],
        "request_id": str(uuid.uuid4()),
        "tray_session_id": str(uuid.uuid4())
    }

    device = {
        "manufacturer": get_prop("ro.product.manufacturer"),
        "model": get_prop("ro.product.model"),
        "device": get_prop("ro.product.device"),
        "android_version": int(get_prop("ro.build.version.sdk") or 33),
        "android_release": get_prop("ro.build.version.release"),
        "dpi": density,
        "resolution": screen_size,
        "refresh_rate": "60.0",
        "cpu": get_prop("ro.product.board"),
        "board": get_prop("ro.product.board"),
        "bootloader": get_prop("ro.bootloader") or "unknown",
        "brand": get_prop("ro.product.brand"),
        "product": get_prop("ro.product.name"),
        "fingerprint": get_prop("ro.build.fingerprint"),
        "radio_version": get_prop("gsm.version.baseband"),
        "build_id": get_prop("ro.build.display.id"),
        "build_tags": get_prop("ro.build.tags"),
        "build_type": get_prop("ro.build.type")
    }

    user_agent = f"Instagram 269.0.0.18.75 Android ({device['android_version']}/{device['android_release']}; {device['dpi']}dpi; {device['resolution']}; {device['brand']}; {device['model']}; {device['device']}; en_US)"

    return {
        "uuids": uuids,
        "device_settings": device,
        "user_agent": user_agent,
        "country": get_prop("persist.sys.country") or "FR",
        "country_code": 261,
        "locale": get_prop("persist.sys.locale") or "fr_FR",
        "timezone_offset": timezone_offset
    }

def creer_config():
    clear()
    titre_section("AJOUTER UN COMPTE")

    username = safe_input("\nNom d'utilisateur Instagram: ").strip()
    password = safe_input("Mot de passe: ").strip()

    if not username or not password:
        erreur("\nChamps obligatoires vides.")
        safe_input("\nAppuyez sur Entrée pour continuer...")
        return

    filepath = os.path.join(CONFIG_DIR, f"{username}.json")

    if os.path.exists(filepath):
        erreur("\nCe compte existe déjà.")
        safe_input("\nAppuyez sur Entrée pour continuer...")
        return

    info_data = get_android_device_info()

    profile = {
        "username": username,
        "password": password,
        "uuid": str(uuid.uuid4()),
        "device_info": info_data["device_settings"],
        "uuids": info_data["uuids"],
        "user_agent": info_data["user_agent"],
        "country": info_data["country"],
        "country_code": info_data["country_code"],
        "locale": info_data["locale"],
        "timezone_offset": info_data["timezone_offset"],
        "last_login": datetime.now().timestamp()
    }

    with open(filepath, 'w') as f:
        json.dump(profile, f, indent=4)

    success(f"\nProfil enregistré pour {username}.")
    log_action("créé", username)
    safe_input("\nAppuyez sur Entrée pour revenir au menu...")

def supprimer_compte():
    clear()
    titre_section("SUPPRIMER UN COMPTE")

    username = safe_input("Nom d'utilisateur à supprimer: ").strip()

    fichiers = [
        os.path.join(CONFIG_DIR, f"{username}.json"),
        os.path.join(SESSION_DIR, f"{username}_session.json")
    ]

    confirm = safe_input(f"\nConfirmer suppression de {username} ? (o/n): ").lower()
    if confirm != 'o':
        print("Annulé.")
        safe_input("\nAppuyez sur Entrée pour revenir au menu...")
        return

    for f in fichiers:
        if os.path.exists(f):
            os.remove(f)
            print(f"\n\033[1;31m[SUPPRIMÉ]\033[0m {f}")

    log_action("supprimé", username)
    safe_input("\nAppuyez sur Entrée pour revenir au menu...")

def lister_comptes():
    clear()
    fichiers = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]

    titre_section("COMPTES ENREGISTRÉS")

    if not fichiers:
        print("\nAucun profil enregistré.")
    else:
        for f in fichiers:
            print(" -", f.replace('.json', ''))

    safe_input("\nAppuyez sur Entrée pour revenir au menu...")

def nettoyer_sessions_orphelines():
    clear()
    titre_section("NETTOYAGE DES SESSIONS ORPHELINES")

    configs = [f.replace('.json', '') for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('_session.json')]

    supprimés = 0
    for session_file in sessions:
        username = session_file.replace('_session.json', '')
        if username not in configs:
            try:
                os.remove(os.path.join(SESSION_DIR, session_file))
                print(f"\n\033[1;33m[SUPPRIMÉ]\033[0m {session_file}")
                supprimés += 1
            except Exception as e:
                erreur(f"\nErreur suppression {session_file}: {e}")

    if supprimés:
        info(f"{supprimés} session(s) supprimée(s).")
    else:
        info("\nAucune session orpheline.")

    safe_input("\nAppuyez sur Entrée pour revenir au menu...")

def menu():
    while True:
        clear()
        titre_section("GESTION DES COMPTES")
        print("\n1. Ajouter un compte")
        print("2. Supprimer un compte")
        print("3. Lister les comptes")
        print("4. Nettoyer les sessions orphelines")
        print("0. Quitter")

        choix = safe_input("\nChoix: ").strip()

        if choix == "1":
            creer_config()
        elif choix == "2":
            supprimer_compte()
        elif choix == "3":
            lister_comptes()
        elif choix == "4":
            nettoyer_sessions_orphelines()
        elif choix == "0":
            print("\nAu revoir.")
            break
        else:
            erreur("\nChoix invalide.")
            safe_input("\nAppuyez sur Entrée...")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nArrêté par l'utilisateur.")
