import os
import json
import uuid
import subprocess

def get_android_info():
    try:
        info = json.loads(subprocess.check_output(['termux-info']).decode())
        android_version = info.get('android_version', '10')
        sdk = info.get('android_sdk', '29')
    except:
        android_version = '10'
        sdk = '29'
    
    return android_version, sdk

def get_resolution():
    try:
        display = json.loads(subprocess.check_output(['termux-display-info']).decode())
        width = display['resolution']['width']
        height = display['resolution']['height']
        return f"{width}x{height}"
    except:
        return "1080x1920"

def create_profile(username):
    android_version, sdk = get_android_info()
    resolution = get_resolution()

    profile = {
        "uuid": str(uuid.uuid4()),
        "android_version": android_version,
        "android_sdk": sdk,
        "device_model": "Android Device",
        "device_brand": "Generic",
        "device_manufacturer": "Generic",
        "resolution": resolution
    }

    config_path = f"scripts/config/{username}.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(profile, f, indent=4)
    print(f"[✓] Profil créé : {config_path}")

# Exemple d'utilisation
username = input("Nom d'utilisateur : ")
create_profile(username)
