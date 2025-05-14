#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from cryptography.fernet import Fernet

# Dossiers & chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG1_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'config1.json'))
ACCOUNTS_DIR = os.path.join(BASE_DIR, "accounts")
HISTORY_PATH = os.path.join(ACCOUNTS_DIR, "history.log")

# Couleurs terminal
def couleur(texte, code): return f"\033[{code}m{texte}\033[0m"
def horloge(): return datetime.now().strftime("[TS %H:%M:%S]")

def info(msg): print(f"{horloge()} {couleur(msg, '1;34')}")
def success(msg): print(f"{horloge()} {couleur(msg, '1;32')}")
def erreur(msg): print(f"{horloge()} {couleur(msg, '1;31')}")

# Historique
def enregistrer_historique(msg):
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)
    with open(HISTORY_PATH, "a") as f:
        f.write(f"{horloge()} {msg}\n")

# Charger et corriger config1.json
def corriger_config_si_necessaire():
    if not os.path.exists(CONFIG1_PATH): return
    with open(CONFIG1_PATH, "r") as f:
        try: data = json.load(f)
        except json.JSONDecodeError: return
    if isinstance(data, list):
        with open(CONFIG1_PATH, "w") as f:
            json.dump({"utilisateurs": data}, f, indent=4)

def lire_utilisateurs_config():
    corriger_config_si_necessaire()
    if not os.path.exists(CONFIG1_PATH): return []
    with open(CONFIG1_PATH, "r") as f:
        try: data = json.load(f)
        except json.JSONDecodeError: return []
    return data.get("utilisateurs", [])

# Ajouter un compte
def ajouter_compte(username, password):
    utilisateurs = lire_utilisateurs_config()
    if any(u["username"] == username for u in utilisateurs):
        erreur("Ce compte existe déjà.")
        return
    utilisateurs.append({"username": username, "password": password})
    with open(CONFIG1_PATH, "w") as f:
        json.dump({"utilisateurs": utilisateurs}, f, indent=4)
    success(f"Compte {username} ajouté.")
    enregistrer_historique(f"[+] Ajout : {username}")

# Supprimer un compte
def supprimer_utilisateur_config(username):
    utilisateurs = lire_utilisateurs_config()
    utilisateurs = [u for u in utilisateurs if u["username"] != username]
    with open(CONFIG1_PATH, "w") as f:
        json.dump({"utilisateurs": utilisateurs}, f, indent=4)
    success(f"{username} supprimé.")
    enregistrer_historique(f"[-] Suppression : {username}")

# Lister les comptes
def lister_comptes():
    utilisateurs = lire_utilisateurs_config()
    if not utilisateurs:
        info("Aucun compte enregistré.")
        return
    print(f"\n{couleur('╔════════════════ LISTE DES COMPTES ════════════════╗', '1;36')}")
    for i, utilisateur in enumerate(utilisateurs, 1):
        print(couleur(f"  {i}. {utilisateur['username']}", "1;37"))
    print(couleur("╚════════════════════════════════════════════════════╝\n", '1;36'))

# Menu interactif
def menu():
    while True:
        os.system("clear")
        print(couleur("╔══════════════════════════════════════════════╗", "1;35"))
        print(couleur("║        GESTION DES COMPTES INSTAGRAM         ║", "1;35"))
        print(couleur("╚══════════════════════════════════════════════╝", "1;35"))
        print()
        print("1. Ajouter un compte")
        print("2. Lister les comptes")
        print("3. Supprimer un compte")
        print("0. Quitter")
        print()
        choix = input(f"{horloge()} {couleur('Choix :', '1;36')} ").strip()

        if choix == "1":
            username = input(couleur("  Nom d'utilisateur : ", "1;37")).strip()
            password = input(couleur("  Mot de passe       : ", "1;37")).strip()
            if username and password:
                ajouter_compte(username, password)
            else:
                erreur("Champs vides non autorisés.")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choix == "2":
            lister_comptes()
            input("Appuyez sur Entrée pour continuer...")

        elif choix == "3":
            utilisateurs = lire_utilisateurs_config()
            if not utilisateurs:
                info("Aucun compte à supprimer.")
                input("Appuyez sur Entrée pour continuer...")
                continue
            lister_comptes()
            cible = input(couleur("Numéro ou nom du compte à supprimer : ", "1;37")).strip()
            if cible.isdigit():
                idx = int(cible) - 1
                if 0 <= idx < len(utilisateurs):
                    username = utilisateurs[idx]["username"]
                else:
                    erreur("Numéro invalide.")
                    input("Appuyez sur Entrée...")
                    continue
            else:
                username = cible
            confirmation = input(f"{couleur('Confirmer la suppression de', '1;31')} {username} ? (o/n) : ").strip().lower()
            if confirmation == "o":
                supprimer_utilisateur_config(username)
            else:
                info("Suppression annulée.")
            input("Appuyez sur Entrée pour continuer...")

        elif choix == "0":
            print(couleur("\nRetour au menu principal...", "1;33"))
            break
        else:
            erreur("Choix invalide.")
            input("Appuyez sur Entrée...")

# Si appelé sans arguments : ouvrir menu
if __name__ == "__main__":
    if len(sys.argv) == 1:
        menu()
    else:
        # Laisser la possibilité d'ajouter/lister/supprimer via ligne de commande
        action = sys.argv[1]
        if action == "add" and len(sys.argv) == 4:
            ajouter_compte(sys.argv[2], sys.argv[3])
        elif action == "list":
            lister_comptes()
        elif action == "delete":
            supprimer_utilisateur_config(sys.argv[2])
        elif action == "purge":
            with open(CONFIG1_PATH, "w") as f:
                json.dump({"utilisateurs": []}, f, indent=4)
            success("Tous les comptes ont été supprimés.")
        else:
            print("Usage :")
            print("  python3 compte_manager.py            (menu interactif)")
            print("  python3 compte_manager.py add <user> <pass>")
            print("  python3 compte_manager.py list")
            print("  python3 compte_manager.py delete <username>")
            print("  python3 compte_manager.py purge")
