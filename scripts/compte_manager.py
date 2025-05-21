import os
import sys
import json
import platform
from datetime import datetime

# Détection du nom de l'appareil
DEVICE_NAME = os.uname().nodename if hasattr(os, 'uname') else platform.node()
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(CONFIG_DIR, f"{DEVICE_NAME}.json")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, "accounts")
HISTORY_PATH = os.path.join(ACCOUNTS_DIR, "history.log")
os.makedirs(ACCOUNTS_DIR, exist_ok=True)

# Couleurs terminal
def couleur(texte, code):
    return f"\033[{code}m{texte}\033[0m"

def horloge():
    return datetime.now().strftime("[TS %H:%M:%S]")

def info(msg):
    print(f"{horloge()} {couleur(msg, '1;34')}")

def success(msg):
    print(f"{horloge()} {couleur(msg, '1;32')}")

def erreur(msg):
    print(f"{horloge()} {couleur(msg, '1;31')}")

def enregistrer_historique(msg):
    with open(HISTORY_PATH, "a") as f:
        f.write(f"{horloge()} {msg}\n")

def corriger_config_si_necessaire():
    if not os.path.exists(CONFIG_PATH):
        return
    with open(CONFIG_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
    if isinstance(data, list):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"utilisateurs": data}, f, indent=4)

def lire_utilisateurs_config():
    corriger_config_si_necessaire()
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return data.get("utilisateurs", [])

def sauvegarder_utilisateurs(utilisateurs):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"utilisateurs": utilisateurs}, f, indent=4)

def ajouter_compte(username, password):
    utilisateurs = lire_utilisateurs_config()
    if any(u["username"] == username for u in utilisateurs):
        erreur("Ce compte existe déjà.")
        return
    utilisateurs.append({"username": username, "password": password})
    sauvegarder_utilisateurs(utilisateurs)
    enregistrer_historique(f"[+] Ajout : {username}")
    success(f"Compte {username} ajouté sans connexion.")

def supprimer_utilisateur_config(username):
    utilisateurs = lire_utilisateurs_config()
    utilisateurs = [u for u in utilisateurs if u["username"] != username]
    sauvegarder_utilisateurs(utilisateurs)
    success(f"{username} supprimé.")
    enregistrer_historique(f"[-] Suppression : {username}")

def lister_comptes():
    utilisateurs = lire_utilisateurs_config()
    if not utilisateurs:
        info("Aucun compte enregistré.")
        return
    print(f"\n{couleur('╔════════════════ LISTE DES COMPTES ════════════════╗', '1;36')}")
    for i, utilisateur in enumerate(utilisateurs, 1):
        print(couleur(f"  {i}. {utilisateur['username']}", "1;37"))
    print(couleur("╚═══════════════════════════════════════════════════╝\n", '1;36'))

def menu():
    while True:
        print(couleur("\n[ MENU COMPTE INSTAGRAM ]", "1;36"))
        print("1. Ajouter un compte")
        print("2. Supprimer un compte")
        print("3. Lister les comptes")
        print("4. Supprimer tous les comptes")
        print("5. Quitter")
        choix = input("\nChoix : ")
        if choix == "1":
            username = input("Nom d'utilisateur : ")
            password = input("Mot de passe : ")
            ajouter_compte(username, password)
        elif choix == "2":
            username = input("Nom du compte à supprimer : ")
            supprimer_utilisateur_config(username)
        elif choix == "3":
            lister_comptes()
        elif choix == "4":
            sauvegarder_utilisateurs([])
            enregistrer_historique("[!] Tous les comptes ont été supprimés.")
            success("Tous les comptes ont été supprimés.")
        elif choix == "5":
            break
        else:
            erreur("Choix invalide.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        menu()
    else:
        action = sys.argv[1]
        if action == "add" and len(sys.argv) == 4:
            ajouter_compte(sys.argv[2], sys.argv[3])
        elif action == "list":
            lister_comptes()
        elif action == "delete" and len(sys.argv) >= 3:
            supprimer_utilisateur_config(sys.argv[2])
        elif action == "purge":
            sauvegarder_utilisateurs([])
            success("Tous les comptes ont été supprimés.")
        else:
            print("Usage :")
            print("  python3 compte_manager.py                (menu interactif)")
            print("  python3 compte_manager.py add USER PASS")
            print("  python3 compte_manager.py list")
            print("  python3 compte_manager.py delete USER")
            print("  python3 compte_manager.py purge")
