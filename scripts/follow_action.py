import json
import time
import os
from instagram_private_api import Client, ClientError

def load_credentials(config_path='config/selected_user.json'):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('username'), config.get('password')
    except Exception as e:
        print(f"[!] Erreur chargement identifiants : {e}")
        return None, None

def load_target(filepath='config/task_data.txt'):
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
        return None
    except Exception as e:
        print(f"[!] Erreur lecture cible : {e}")
        return None

def remove_target_from_file(target_id, filepath='config/task_data.txt'):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        with open(filepath, 'w') as f:
            for line in lines:
                if line.strip() != target_id:
                    f.write(line)
    except Exception as e:
        print(f"[!] Erreur suppression ID : {e}")

def save_action_log(user_id, status, log_path='logs/actions.log'):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    with open(log_path, 'a') as f:
        f.write(f"{timestamp} | Follow {user_id} | {status}\n")

def follow_target_by_id(username, password, target_user_id):
    try:
        api = Client(username, password)
        api.friendships_create(target_user_id)
        print(f"[✓] Suivi réussi de l'ID: {target_user_id}")
        save_action_log(target_user_id, "SUCCESS")
        remove_target_from_file(target_user_id)
    except ClientError as e:
        print(f"[!] Échec du follow : {e}")
        save_action_log(target_user_id, f"ERROR: {e}")

if __name__ == '__main__':
    username, password = load_credentials()
    if not username or not password:
        exit(1)

    target_id = load_target()
    if not target_id:
        print("[!] Aucune ID trouvée dans task_data.txt")
        exit(1)

    follow_target_by_id(username, password, target_id)
