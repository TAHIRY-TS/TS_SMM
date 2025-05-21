#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import uuid
import time
import subprocess
import re
from datetime import datetime
from instagram_private_api import Client, ClientError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
HISTORY_PATH = os.path.join(BASE_DIR, "history.log")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

def horloge():
    return datetime.now().strftime("[TS %H:%M:%S]")

def log_action(msg):
    with open(HISTORY_PATH, 'a') as log_file:
        log_file.write(f"{horloge()} {msg}\n")

def success(msg):
    print(f"{horloge()} \033[1;32m{msg}\033[0m")

def erreur(msg):
    print(f"{horloge()} \033[1;31m{msg}\033[0m")

def info(msg):
    print(f"{horloge()} \033[1;34m{msg}\033[0m")

def get_prop(prop):
    try:
        return subprocess.check_output(['getprop', prop], encoding='utf-8').strip()
    except Exception:
        return ''

def get_android_device_info():
    try:
        screen_size = subprocess.check_output(['wm', 'size'], encoding='utf-8').strip().split()[-1]
    except Exception:
        screen_size = '1080x1920'

    try:
        dpi_output = subprocess.check_output(['dumpsys', 'display'], encoding='utf-8')
        match = re.search(r'Physical density: (\d+)', dpi_output)
        density = match.group(1) if match else '420'
    except Exception:
        density = '420'

    timezone_offset = int((datetime.now() - datetime.utcnow()).total_seconds())

    return {
        'android_version': get_prop('ro.build.version.release'),
        'device_model': get_prop('ro.product.model'),
        'device_brand': get_prop('ro.product.brand'),
        'device_manufacturer': get_prop('ro.product.manufacturer'),
        'screen_resolution': screen_size,
        'screen_density': density,
        'build_tags': get_prop('ro.build.tags'),
        'build_type': get_prop('ro.build.type'),
        'country': get_prop('persist.sys.country') or "FR",
        'country_code': get_prop('gsm.operator.numeric') or get_prop('ro.csc.country_code') or "261",
        'locale': get_prop('persist.sys.locale') or "fr_FR",
        'timezone_offset': timezone_offset
    }

def generate_device_profile():
    info_device = get_android_device_info()

    version_sdk = get_prop("ro.build.version.sdk") or "0"
    model = info_device['device_model'] or "UnknownModel"
    manufacturer = info_device['device_manufacturer'] or "UnknownManufacturer"
    brand = info_device['device_brand'] or "UnknownBrand"
    device = get_prop("ro.product.device") or "UnknownDevice"
    board = get_prop("ro.product.board") or "UnknownBoard"
    release = info_device['android_version'] or "UnknownRelease"
    fingerprint = get_prop("ro.build.fingerprint") or "UnknownFingerprint"
    build_id = get_prop("ro.build.id") or "UnknownBuildID"
    build_tags = info_device['build_tags'] or "UnknownBuildTags"
    resolution = info_device['screen_resolution']
    dpi = info_device['screen_density']

    return {
        "device_settings": {
            "user_agent": f"Instagram 269.0.0.18.75 Android ({version_sdk}/{release}; {dpi}dpi; {resolution}; {manufacturer}; {model}; {device}; mt6765)",
            "manufacturer": manufacturer,
            "model": model,
            "device": device,
            "android_version": int(version_sdk) if version_sdk.isdigit() else 0,
            "android_release": release,
            "dpi": dpi,
            "resolution": resolution,
            "refresh_rate": "60.0",
            "cpu": board,
            "board": board,
            "bootloader": "unknown",
            "brand": brand,
            "product": device,
            "fingerprint": fingerprint,
            "radio_version": "MODEM 228",
            "build_id": build_id,
            "build_tags": build_tags,
            "build_type": info_device['build_type'],
            "country": info_device['country'],
            "country_code": int(info_device['country_code']) if info_device['country_code'].isdigit() else 261,
            "locale": info_device['locale'],
            "timezone_offset": info_device['timezone_offset']
        },
        "uuids": {
            "uuid": str(uuid.uuid4()),
            "phone_id": str(uuid.uuid4()),
            "client_session_id": str(uuid.uuid4()),
            "advertising_id": str(uuid.uuid4()),
            "android_device_id": f"android-{uuid.uuid4().hex[:16]}",
            "request_id": str(uuid.uuid4()),
            "tray_session_id": str(uuid.uuid4()),
            "mid": f"a{uuid.uuid4().hex[:13].upper()}",
            "ig_u_rur": None,
            "ig_www_claim": "0",
            "authorization_data": {
                "ds_user_id": str(uuid.uuid4().int)[:11],
                "sessionid": f"{uuid.uuid4().int % 99999999999}%3A{uuid.uuid4().hex}%3A8%3AAY{uuid.uuid4().hex}",
                "cookies": {
                    "csrftoken": uuid.uuid4().hex[:32]
                }
            },
            "last_login": time.time()
        }
    }

def save_config(username, password):
    data = {
        "username": username,
        "password": password,
        **generate_device_profile()
    }
    path = os.path.join(CONFIG_DIR, f"{username}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    log_action(f"[+] Ajout du compte : {username}")
    success(f"Profil {username} ajouté.")

def login_account(username, password):
    try:
        api = Client(username, password)
        session_file = os.path.join(SESSION_DIR, f"{username}_session.json")
        with open(session_file, 'w') as f:
            f.write(json.dumps(api.settings))
        log_action(f"[SUCCESS] Connexion réussie : {username}")
        success(f"Connexion réussie pour {username}.")
        return True
    except ClientError as e:
        erreur(f"[FAIL] Échec de connexion pour {username} : {e}")
        return False

def add_account():
    username = input("Nom d'utilisateur Instagram: ")
    password = input("Mot de passe: ")
    save_config(username, password)
    login_account(username, password)

def test_accounts():
    files = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    for file in files:
        with open(os.path.join(CONFIG_DIR, file), 'r') as f:
            data = json.load(f)
        username = data.get('username')
        password = data.get('password')
        if username and password:
            print(f"Test de {username}...")
            login_account(username, password)

def delete_account():
    username = input("Nom d'utilisateur à supprimer: ")
    config_path = os.path.join(CONFIG_DIR, f"{username}.json")
    session_path = os.path.join(SESSION_DIR, f"{username}_session.json")
    if os.path.exists(config_path):
        os.remove(config_path)
    if os.path.exists(session_path):
        os.remove(session_path)
    log_action(f"[-] Compte supprimé : {username}")
    success(f"{username} supprimé.")

def list_accounts():
    files = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]
    if not files:
        info("Aucun compte trouvé.")
    else:
        print("\n\033[1;36m╔══════════ COMPTES ENREGISTRÉS ══════════╗\033[0m")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.replace('.json', '')}")
        print("\033[1;36m╚═════════════════════════════════════════╝\033[0m\n")

def extract_session(username):
    path = os.path.join(CONFIG_DIR, f"{username}.json")
    if not os.path.exists(path):
        erreur("Ce compte n'existe pas.")
        return
    with open(path, "r") as f:
        data = json.load(f)
    auth = data.get("uuids", {}).get("authorization_data", {})
    sessionid = auth.get("sessionid", "N/A")
    ds_user_id = auth.get("ds_user_id", "N/A")
    csrftoken = auth.get("cookies", {}).get("csrftoken", "N/A")

    print(f"\n\033[1;35m╔═══════════ SESSION POUR {username} ═══════════╗\033[0m")
    print(f"  Session ID   : {sessionid}")
    print(f"  DS User ID   : {ds_user_id}")
    print(f"  CSRF Token   : {csrftoken}")
    print("\033[1;35m╚═══════════════════════════════════════════════╝\033[0m\n")

def main_menu():
    while True:
        print("\n\033[1;36m╔═════════════════════════════════════════╗\033[0m")
        print("\033[1;36m|           GESTION DE COMPTES           |\033[0m")
        print("\033[1;36m╚═════════════════════════════════════════╝\033[0m")
        print("1. Ajouter un compte")
        print("2. Tester les comptes")
        print("3. Supprimer un compte")
        print("4. Lister les comptes")
        print("5. Extraire session")
        print("0. Quitter")
        choix = input("Choix: ")
        if choix == '1':
            add_account()
        elif choix == '2':
            test_accounts()
        elif choix == '3':
            delete_account()
        elif choix == '4':
            list_accounts()
        elif choix == '5':
            username = input("Nom d'utilisateur: ")
            extract_session(username)
        elif choix == '0':
            break
        else:
            erreur("Choix invalide.")

if __name__ == '__main__':
    main_menu()
