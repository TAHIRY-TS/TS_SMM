import json
import time
import random
import re
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
print( "🥰UNE GRANDE SURPRISE🥰")
print("😎ICI C'EST AUTOFOLLOWERS🤓")
print("🤒Alos commençons🤗")
# === Chemins globaux ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "scripts", "config", "config1.json")
SELECTED_USER_PATH = os.path.join(PROJECT_ROOT, "config", "selected_user1.json")
TASK_LOG_PATH = os.path.join(PROJECT_ROOT, "config", "task_data1.txt")
ERROR_LOG_PATH = os.path.join(PROJECT_ROOT, "logs", "errors.txt")
DAILY_LOG_PATH = os.path.join(PROJECT_ROOT, "logs", f"{datetime.now().date()}.txt")

# === Fonctions utilitaires ===

def log_error(message):
    with open(ERROR_LOG_PATH, "a") as errlog:
        errlog.write(f"{datetime.now()} - {message}\n")

def log_daily(message):
    with open(DAILY_LOG_PATH, "a") as log:
        log.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

def clean_temp_files():
    if os.path.exists(SELECTED_USER_PATH):
        os.remove(SELECTED_USER_PATH)

def extract_username_from_url(url):
    match = re.match(r'https?://(www\.)?instagram\.com/([^/?#&]+)', url)
    return match.group(2) if match else None

def login_and_follow(account, target_username):
    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = uc.Chrome(options=options)
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        # Connexion
        driver.find_element(By.NAME, 'username').send_keys(account['username'])
        driver.find_element(By.NAME, 'password').send_keys(account['password'], Keys.RETURN)
        time.sleep(7)

        # Accès au profil
        driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(5)

        # Vérifier déjà abonné
        try:
            driver.find_element(By.XPATH, "//button[contains(text(), 'Abonné') or contains(text(), 'Demandé')]")
            print(f"[INFO] {account['username']} est déjà abonné à {target_username}")
            return "deja"
        except:
            follow_button = driver.find_element(By.XPATH, "//button[text()='Suivre']")
            follow_button.click()
            print(f"[OK] {account['username']} a suivi {target_username}")
            return "suivi"
    except Exception as e:
        log_error(f"{account['username']} - {str(e)}")
        print(f"[ERREUR] {account['username']} - {str(e)}")
        return "erreur"
    finally:
        try:
            driver.quit()
        except:
            pass

# === Script principal ===

def main():
    try:
        with open(CONFIG_PATH, "r") as f:
            accounts = json.load(f)["utilisateur"]
    except Exception as e:
        print("[!] Erreur de lecture du fichier config1.json")
        log_error(str(e))
        return

    url = input("Colle le lien Instagram cible : ").strip()
    target_username = extract_username_from_url(url)
    if not target_username:
        print("[!] Lien invalide.")
        return

    # Enregistrer temporairement le compte cible
    with open(SELECTED_USER_PATH, "w") as sel:
        json.dump({"target": target_username}, sel)

    try:
        nb_followers = int(input("Nombre de comptes à utiliser : "))
    except:
        print("[!] Nombre invalide.")
        return

    random.shuffle(accounts)
    used_accounts = []
    success_count = 0

    for acc in accounts:
        if success_count >= nb_followers:
            break
        if acc in used_accounts:
            continue
        used_accounts.append(acc)
        result = login_and_follow(acc, target_username)
        if result == "suivi":
            success_count += 1
        time.sleep(random.randint(10, 20))

    # Historique
    with open(TASK_LOG_PATH, "a") as task:
        task.write(f"{datetime.now()} - {target_username} : {success_count} abonnés\n")

    log_daily(f"{success_count} comptes ont suivi {target_username}")
    clean_temp_files()
    print(f"[FIN] {success_count} comptes ont suivi {target_username}")

if __name__ == "__main__":
    main()
