import os
import json
import uuid
import subprocess
from datetime import datetime
from instagram_private_api import Client, ClientError

CONFIG_DIR = 'config'
SESSION_DIR = 'sessions'
LOG_FILE = 'history.log'

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

def get_device_info():
    try:
        props = subprocess.check_output("getprop", shell=True).decode()
        def prop(key): return next((line.split(":")[1].strip(" []") for line in props.splitlines() if key in line), "")
        return {
            "android_version": prop("ro.build.version.release"),
            "model": prop("ro.product.model"),
            "manufacturer": prop("ro.product.manufacturer"),
            "brand": prop("ro.product.brand"),
            "device": prop("ro.product.device"),
            "hardware": prop("ro.hardware"),
            "build_id": prop("ro.build.display.id"),
            "dpi": "420dpi",
            "resolution": "1080x1920"
        }
    except Exception as e:
        return {}

def info(msg): print(f"[INFO] {msg}")
def erreur(msg): print(f"[ERREUR] {msg}")
def succes(msg): print(f"[SUCCÈS] {msg}")

def enregistrer_historique(action, username):
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {action.upper()} - {username}\n")

def creer_config():
    username = input("Nom d'utilisateur Instagram: ").strip()
    password = input("Mot de passe: ").strip()
    if not username or not password:
        erreur("Champs obligatoires vides.")
        return

    filepath = os.path.join(CONFIG_DIR, f"{username}.json")
    if os.path.exists(filepath):
        erreur("Ce compte existe déjà.")
        return

    device_info = get_device_info()
    profile = {
        "username": username,
        "password": password,
        "uuid": str(uuid.uuid4()),
        "device_info": device_info
    }

    with open(filepath, 'w') as f:
        json.dump(profile, f, indent=4)

    succes(f"Profil sauvegardé dans {filepath}.")
    enregistrer_historique("créé", username)

def tester_connexion():
    username = input("Nom d'utilisateur à tester: ").strip()
    config_file = os.path.join(CONFIG_DIR, f"{username}.json")
    if not os.path.exists(config_file):
        erreur("Aucun profil trouvé.")
        return

    with open(config_file) as f:
        profil = json.load(f)

    try:
        session_file = os.path.join(SESSION_DIR, f"{username}_session.json")
        api = Client(profil["username"], profil["password"])
        with open(session_file, 'w') as f:
            json.dump(api.settings, f)
        succes(f"Connexion réussie. Session enregistrée dans {session_file}.")
        enregistrer_historique("connecté", username)
    except ClientError as e:
        erreur(f"Erreur Instagram : {e}")
    except Exception as e:
        erreur(f"Erreur : {e}")

def supprimer_compte():
    username = input("Nom d'utilisateur à supprimer: ").strip()
    fichiers = [
        os.path.join(CONFIG_DIR, f"{username}.json"),
        os.path.join(SESSION_DIR, f"{username}_session.json")
    ]
    confirm = input(f"Confirmer suppression de {username} ? (o/n): ").lower()
    if confirm != 'o':
        print("Annulé.")
        return

    for f in fichiers:
        if os.path.exists(f):
            os.remove(f)
            print(f"[SUPPRIMÉ] {f}")
    enregistrer_historique("supprimé", username)

def lister_comptes():
    fichiers = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    if not fichiers:
        print("Aucun profil.")
        return
    print("\nProfils enregistrés:")
    for f in fichiers:
        print(" -", f.replace('.json', ''))

def nettoyer_sessions_orphelines():
    configs = [f.replace('.json', '') for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]
    sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('_session.json')]
    supprimés = 0
    for session_file in sessions:
        username = session_file.replace('_session.json', '')
        if username not in configs:
            try:
                os.remove(os.path.join(SESSION_DIR, session_file))
                print(f"  [SUPPRIMÉ] {session_file}")
                supprimés += 1
            except Exception as e:
                erreur(f"Erreur suppression {session_file}: {e}")
    if supprimés:
        info(f"{supprimés} session(s) orpheline(s) supprimée(s).")
    else:
        info("Aucune session orpheline.")

def menu():
    while True:
        print("\n--- MENU ---")
        print("1. Ajouter un compte")
        print("2. Tester une connexion")
        print("3. Supprimer un compte")
        print("4. Lister les comptes")
        print("5. Nettoyer sessions orphelines")
        print("0. Quitter")
        choix = input("Choix: ")

        if choix == "1":
            creer_config()
        elif choix == "2":
            tester_connexion()
        elif choix == "3":
            supprimer_compte()
        elif choix == "4":
            lister_comptes()
        elif choix == "5":
            nettoyer_sessions_orphelines()
        elif choix == "0":
            print("Au revoir.")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu()
