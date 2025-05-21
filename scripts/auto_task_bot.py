import os
import json
import re
import asyncio
import subprocess
import random
import hashlib
from datetime import datetime
from telethon.sync import TelegramClient, events

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def horloge_prefix():
    return color(f"[TS {datetime.now().strftime('%H:%M')}]", "1;34") + " "

# Répertoires
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
CONFIG_DIR = os.path.join(PROJECT_DIR, 'scripts', 'config')
CONFIG_USERS_PATH = CONFIG_DIR  # Le dossier contient tous les *.json utilisateurs
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
SELECTED_USER_PATH = os.path.join(CONFIG_DIR, 'selected_user.json')
TASK_FILE_PATH = os.path.join(CONFIG_DIR, 'task_data.txt')
LOGS_DIR = os.path.join(SCRIPT_DIR, 'logs')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
FOLLOW_SCRIPT_PATH = os.path.join(DATA_DIR, 'follow_action.py')
LIKE_SCRIPT_PATH = os.path.join(DATA_DIR, 'like_action.py')
ERROR_LOG_PATH = os.path.join(LOGS_DIR, 'errors.txt')

os.makedirs(LOGS_DIR, exist_ok=True)

# Chargement config principale
try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
        api_id = config["api_id"]
        api_hash = config["api_hash"]
        min_delay = config.get("min_delay", 5)
        max_delay = config.get("max_delay", 15)
except Exception as e:
    with open(ERROR_LOG_PATH, "a") as f:
        f.write(f"[CONFIG ERROR] {datetime.now()} - {e}\n")
    raise SystemExit("[❌] Erreur lors du chargement de la configuration principale.")

# Chargement utilisateurs depuis scripts/config/*.json
def charger_utilisateurs():
    utilisateurs = []
    for fichier in os.listdir(CONFIG_USERS_PATH):
        if fichier.endswith(".json") and fichier not in ["config.json", "selected_user.json", "task_data.txt"]:
            chemin = os.path.join(CONFIG_USERS_PATH, fichier)
            try:
                with open(chemin, encoding="utf-8") as f:
                    data = json.load(f)
                    if "username" in data and "password" in data:
                        utilisateurs.append(data)
            except Exception as e:
                with open(ERROR_LOG_PATH, "a") as err:
                    err.write(f"[UTILISATEUR LOAD ERROR] {fichier} : {e}\n")
    return utilisateurs

utilisateurs = charger_utilisateurs()
utilisateur_actuel = 0

client = TelegramClient("session_smmkingdom", api_id, api_hash)

# Extraction infos tâche
def extraire_infos(message):
    lien_match = re.search(r'https://www\.instagram\.com/([a-zA-Z0-9_.]+)/', message)
    action_match = re.search(r'Action\s*:\s*(Follow|Like)', message, re.IGNORECASE)
    if lien_match and action_match:
        username = lien_match.group(1)
        action = action_match.group(1).strip().lower()
        return username, lien_match.group(0), action
    return None, None, None

# Logs
def journaliser(message):
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_file = os.path.join(LOGS_DIR, f"{date_str}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def log_erreur(erreur):
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {erreur}\n")

# Envoyer tâche
async def envoyer_tache():
    global utilisateur_actuel
    if utilisateur_actuel >= len(utilisateurs):
        utilisateur_actuel = 0
    await asyncio.sleep(random.randint(min_delay, max_delay))
    try:
        await client.send_message("SmmKingdomTasksBot", "📝Tasks📝")
    except Exception as e:
        log_erreur(f"Erreur envoi 📝Tasks📝 : {e}")

# Exécuter action
def executer_action(action):
    try:
        script_path = FOLLOW_SCRIPT_PATH if "follow" in action else LIKE_SCRIPT_PATH
        subprocess.run(["python3", script_path], check=True)
    except Exception as e:
        log_erreur(f"Erreur executer_action({action}) : {e}")

# Nettoyage
async def nettoyage_fichiers():
    for path in [TASK_FILE_PATH, SELECTED_USER_PATH]:
        try:
            with open(path, "w") as f:
                pass
        except Exception as e:
            log_erreur(f"[Nettoyage fichier {path}] {e}")

# Gestion des messages Telegram
@client.on(events.NewMessage(from_users="SmmKingdomTasksBot"))
async def handle_message(event):
    global utilisateur_actuel
    try:
        message = event.message.message.strip()
        journaliser(message)

        if "My Balance" in message:
            match = re.search(r"My Balance\s*:\s*\*\*(\d+(\.\d+)?)\s*cashCoins", message)
            if match:
                solde = match.group(1)
                print(f"[💵] Votre solde actuel : {solde} cashCoins")
            await asyncio.sleep(3)
            await event.respond("📝Tasks📝")
            return

        if "Choose social network" in message:
            await asyncio.sleep(3)
            await event.respond("Instagram")
            return

        if "no active tasks" in message.lower() or "⭕️ Sorry" in message:
            print(horloge_prefix() + color("[⛔] Aucun tâche sur ce compte", "1;33"))
            await asyncio.sleep(3)
            await event.respond("Instagram")
            return

        if any(phrase in message for phrase in [
            "Current status of this account is Limited.",
            "Please choose account",
            "username for tasks"
        ]):
            if utilisateur_actuel >= len(utilisateurs):
                utilisateur_actuel = 0
            user = utilisateurs[utilisateur_actuel]
            utilisateur_actuel += 1
            print(horloge_prefix() + color(f"[→] Username : {user['username']}", "1;36"))
            with open(SELECTED_USER_PATH, 'w') as su:
                json.dump(user, su)
            await asyncio.sleep(3)
            await event.respond(user["username"])
            return

        if "Link" in message and ("Follow" in message or "Like" in message):
            username, lien, action = extraire_infos(message)
            if username and lien:
                task_id = hashlib.md5(lien.encode()).hexdigest()[:10]
                with open(TASK_FILE_PATH, "w") as f:
                    f.write(task_id)

                emoji, couleur = ("➕", "1;36") if action == "follow" else ("❤️", "1;31")
                print(horloge_prefix() + color(f"{emoji} Tâche : {lien} | ID : {task_id} | Action : {action.upper()}", couleur))

                executer_action(action)
                await event.respond("✅Completed")
                await envoyer_tache()
                await nettoyage_fichiers()
                return

    except Exception as e:
        log_erreur(f"[handle_message ERROR] {e}")

# Main
async def main():
    try:
        await client.start()
        print(horloge_prefix() + color("[✓] Connecté à Telegram.", "1;32"))
        await envoyer_tache()
        await client.run_until_disconnected()
    except Exception as e:
        log_erreur(f"[main ERROR] {e}")

with client:
    client.loop.run_until_complete(main())
