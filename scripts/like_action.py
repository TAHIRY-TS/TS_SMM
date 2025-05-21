import json
import time
from instagram_private_api import Client, ClientError
import os

def load_credentials(config_path='config/selected_user.json'):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get('username'), config.get('password')

def load_target_media_id(task_path='config/task_data.txt'):
    with open(task_path, 'r') as f:
        media_id = f.read().strip()
    return media_id

def save_action_log(media_id, status, log_path='logs/actions.log'):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log_line = f"{timestamp} | Like {media_id} | {status}\n"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(log_line)

def like_media(media_id):
    username, password = load_credentials()
    try:
        api = Client(username, password)
    except ClientError as e:
        print(f"Erreur de connexion: {e}")
        return False

    try:
        api.post_like(media_id)
        print(f"Like sur le média {media_id} réussi !")
        save_action_log(media_id, 'SUCCESS')
        return True
    except ClientError as e:
        print(f"Échec du like sur {media_id}: {e}")
        save_action_log(media_id, f'ERROR: {e}')
        return False

if __name__ == '__main__':
    media_id = load_target_media_id()
    like_media(media_id)
