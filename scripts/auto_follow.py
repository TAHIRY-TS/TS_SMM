import os
import json
import re
import uuid
import pickle
import time
import random
import hashlib
from datetime import datetime
from instagram_private_api import Client, ClientError, ClientCookieExpiredError, ClientLoginRequiredError

# === Chemins ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "config1.json")
SESSION_DIR = os.path.join(PROJECT_ROOT, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

# === Fonctions sessions ===
def generate_device_seed(username):
    seed = hashlib.md5(username.encode()).hexdigest()
    return {
        'device_id': f'android-{seed[:16]}',
        'uuid': str(uuid.uuid5(uuid.NAMESPACE_DNS, seed)),
        'phone_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, seed + "phone")),
        'session_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, seed + "session"))
    }

def save_session(api, username):
    with open(os.path.join(SESSION_DIR, f"{username}.session"), 'wb') as f:
        pickle.dump(api.settings, f)

def load_session(username):
    path = os.path.join(SESSION_DIR, f"{username}.session")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None

def login(account):
    seed = generate_device_seed(account['username'])
    session = load_session(account['username'])
    try:
        if session:
            api = Client(account['username'], account['password'], settings=session)
        else:
            api = Client(account['username'], account['password'], device_id=seed['device_id'])
            save_session(api, account['username'])
        return api
    except (ClientCookieExpiredError, ClientLoginRequiredError):
        try:
            api = Client(account['username'], account['password'], device_id=seed['device_id'])
            save_session(api, account['username'])
            return api
        except Exception as e:
            print(f"[ERREUR] {account['username']} : {e}")
            return None
    except Exception as e:
        print(f"[ERREUR] {account['username']} : {e}")
        return None

def follow(api, username, account_username):
    try:
        user_id = api.username_info(username)['user']['pk']
        api.friendships_create(user_id)
        print(f"[OK] {account_username} a suivi {username}")
        return True
    except ClientError as e:
        print(f"[ERREUR] {account_username} : {e}")
        return False

# === Script principal ===
def main():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
        accounts = data["utilisateurs"]

    url = input("Colle le lien Instagram cible : ").strip()
    match = re.match(r'https?://(www\.)?instagram\.com/([^/?#&]+)', url)
    if not match:
        print("[!] Lien invalide.")
        return
    target = match.group(2)

    nb = int(input("Nombre de comptes à utiliser : "))
    random.shuffle(accounts)
    used = 0

    for acc in accounts:
        if used >= nb:
            break
        api = login(acc)
        if api and follow(api, target, acc['username']):
            used += 1
        time.sleep(random.randint(5, 10))

    print(f"[FIN] {used} comptes ont suivi {target}")

if __name__ == "__main__":
    main()
