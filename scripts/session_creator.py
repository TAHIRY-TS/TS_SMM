import os, json, random, time
from instagram_private_api import Client, ClientError

# Couleurs terminal
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
B = '\033[94m'; C = '\033[96m'; W = '\033[0m'

# Dossiers
BASE = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE, 'config')

def get_profiles():
    return [f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]

def load_profile(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_session(path, settings):
    with open(path, 'w') as f:
        json.dump(settings, f)

def try_login(data, session_file):
    try:
        device = data['device_settings']
        user_agent = data['user_agent']
        uuids = data['uuids']
        username = data['username']
        password = data['password']

        api = Client(
            username, password,
            device_id=uuids['android_device_id'],
            guid=uuids['uuid'],
            phone_id=uuids['phone_id'],
            user_agent=user_agent,
            device=device
        )
        save_session(session_file, api.settings)
        print(f"{G}[✓] Connexion réussie : {username}{W}")
        return api
    except ClientError as e:
        print(f"{R}[✗] Erreur de connexion : {e}{W}")
        return None

def load_random_session():
    files = get_profiles()
    if not files:
        print(f"{R}[!] Aucun profil JSON trouvé dans {CONFIG_DIR}{W}")
        return None

    profile = random.choice(files)
    json_path = os.path.join(CONFIG_DIR, profile)
    session_path = json_path.replace('.json', '.session')

    data = load_profile(json_path)
    username = data['username']

    print(f"{Y}[*] Tentative de chargement du profil : {username}...{W}")
    time.sleep(3)  # Pause de 3 secondes

    if os.path.exists(session_path):
        try:
            with open(session_path, 'r') as f:
                session = json.load(f)
            api = Client(username, data['password'], settings=session)
            api.current_user()
            print(f"{C}[•] Session valide : {username}{W}")
            return api
        except Exception:
            print(f"{Y}[!] Session expirée ou corrompue : {username}{W}")
            os.remove(session_path)

    print(f"{B}[*] Reconnexion à {username}...{W}")
    return try_login(data, session_path)

if __name__ == '__main__':
    print(f"{C}--- Chargement d'une session Instagram aléatoire ---{W}")
    api = load_random_session()

    if api:
        me = api.current_user()
        print(f"{G}[✓] Utilisateur connecté : @{me['user']['username']}{W}")
    else:
        print(f"{R}[!] Aucun compte n'a pu être connecté.{W}")

    input(f"\n{Y}Appuie sur Entrée pour revenir au menu...{W}")
