from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from datetime import datetime
import os
import json
import time
import subprocess

# Fonction horloge stylée
def horloge():
    return f"\033[1;36m[TS {datetime.now().strftime('%H:%M:%S')}]\033[0m"

# Animation de chargement
def loading_animation(message="Connexion"):
    print(f"{horloge()} \033[1;36m{message}\033[0m", end="")
    for _ in range(3):
        print(".", end="", flush=True)
        time.sleep(0.5)
    print()

# Création du dossier config si inexistant
os.makedirs("config", exist_ok=True)

def lancer_tasks():
    print(f"{horloge()} \033[1;32mLancement de l'autoclick...\033[0m")
    subprocess.run(["python3", "scripts/tasks.py"])

def se_connecter_et_sauvegarder(api_id, api_hash, phone):
    try:
        with TelegramClient(StringSession(), api_id, api_hash) as client:
            client.start(phone)
            session_string = client.session.save()
            config = {
                "api_id": api_id,
                "api_hash": api_hash,
                "session": session_string
            }
            with open("config/config.json", "w") as f:
                json.dump(config, f, indent=4)
            print(f"{horloge()} \033[1;32mConnexion réussie et session sauvegardée\033[0m")
            lancer_tasks()
    except Exception as e:
        print(f"{horloge()} \033[1;31mErreur de connexion : {e}\033[0m")

# Tentative de lecture de config existante
try:
    with open("config/config.json") as f:
        data = json.load(f)
        api_id = data["api_id"]
        api_hash = data["api_hash"]
        session_str = data["session"]
    print(f"{horloge()} \033[1;33mConnexion avec les identifiants existants...\033[0m")
    loading_animation()
    with TelegramClient(StringSession(session_str), api_id, api_hash) as client:
        client.connect()
        if client.is_user_authorized():
            print(f"{horloge()} \033[1;32mConnexion réussie avec la session existante.\033[0m")
            lancer_tasks()
        else:
            raise Exception("Session expirée ou invalide.")
except Exception as e:
    print(f"{horloge()} \033[1;31mAucune session valide. Veuillez entrer vos informations Telegram.\033[0m")
    api_id = int(input(f"{horloge()} Entrez votre \033[1;36mAPI ID\033[0m Telegram : "))
    api_hash = input(f"{horloge()} Entrez votre \033[1;36mAPI HASH\033[0m Telegram : ")
    phone = input(f"{horloge()} Entrez votre \033[1;36mNuméro de téléphone\033[0m : ")
    loading_animation("Connexion en cours")
    se_connecter_et_sauvegarder(api_id, api_hash, phone)
