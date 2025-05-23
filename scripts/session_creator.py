import os
import json
import time
from instagram_private_api import Client, ClientError
import requests  # pour envoyer les notifications Telegram

# Couleurs
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'

BASE = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE, 'config', 'user.json')
BOT_TOKEN_PATH = os.path.join(BASE, 'config', 'bot_token.json')

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def send_telegram_message(text):
    try:
        data = load_json(BOT_TOKEN_PATH)
        token = data["bot_token"]
        chat_id = data["chat_id"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"{R}Erreur Telegram: {e}{W}")

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
