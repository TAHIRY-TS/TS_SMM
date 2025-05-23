import os
import json
import time
from instagram_private_api import Client, ClientError
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Couleurs
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'

BASE = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE, 'config', 'user.json')


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def send_telegram_message(text):
    try:
        tg_data = load_json(os.path.join(BASE, 'config.json'))
        client = TelegramClient(tg_data["session_name"], tg_data["api_id"], tg_data["api_hash"])
 
               client.start()  # Demande ton numéro et code à la première exécution

        with client:
            client.send_message('me', text)  # Message à toi-même (tu peux changer pour un @pseudo)
            print(f"{C}[Telegram] Notification envoyée !{W}")
    except SessionPasswordNeededError:
        print(f"{R}Erreur : Mot de passe 2FA requis dans Telegram.{W}")
    except Exception as e:
        print(f"{R}Erreur Telethon : {e}{W}")
def connect_with_auth_data(data):
    try:
        auth = data["authorization_data"]
        api = Client(
            data["username"], data["password"],
            user_agent=data["user_agent"],
            device_id=auth["device_id"],
            guid=auth["uuid"],
            phone_id=auth["phone_id"]
        )
        api.current_user()
        print(f"{G}[✓] Session active : @{data['username']}{W}")
        send_telegram_message(f"[IG] Session prête pour @{data['username']}")
        return api
    except ClientError as e:
        print(f"{R}[✗] Connexion échouée : {e}{W}")
        send_telegram_message(f"[IG] Erreur connexion @{data['username']}: {e}")
        return None

if __name__ == '__main__':
    print(f"{C}--- Connexion via authorization_data ---{W}")
    data = load_json(CONFIG_PATH)
    api = connect_with_auth_data(data)
    if api:
        # Ici, on ajoutera l'exécution automatique des tâches SMM
        print(f"{Y}[!] Prêt à exécuter les tâches SMM pour @{data['username']}{W}")
