#!/data/data/com.termux/files/usr/bin/bash

# Vérification de l'utilisateur
if [ -z "$1" ]; then
    echo -e "\033[1;31m[!] Utilisation : ./user_agent.sh <username>\033[0m"
    exit 1
fi

username="$1"
json_path="scripts/config/${username}.json"

# Génération du User-Agent
echo -e "\033[1;32m[•] Génération automatique du User-Agent Instagram réel...\033[0m"

android_version=$(getprop ro.build.version.sdk)
android_release=$(getprop ro.build.version.release)
dpi=$(wm density | grep -o '[0-9]*')
resolution=$(wm size | grep -o '[0-9]*x[0-9]*')
manufacturer=$(getprop ro.product.manufacturer | tr '[:upper:]' '[:lower:]')
device=$(getprop ro.product.device)
model=$(getprop ro.product.model | sed 's/ /_/g')
chipset=$(getprop ro.board.platform)
lang=$(getprop persist.sys.locale)
lang=${lang:-en_US}

app_version=$(dumpsys package com.instagram.android | grep versionName | awk -F= '{print $2}')
version_code=$(dumpsys package com.instagram.android | grep versionCode | head -n1 | awk '{print $2}')

user_agent="Instagram $app_version Android ($android_version/$android_release; ${dpi}dpi; $resolution; $manufacturer; $device; $model; $chipset; $lang; $version_code)"

# Affichage
echo -e "\n\033[1;36mUser-Agent:\033[0m"
echo "$user_agent"

# Insertion dans le JSON
if [ -f "$json_path" ]; then
    echo -e "\033[1;33m[•] Insertion dans : $json_path\033[0m"

    # Ajoute ou remplace la clé "user_agent"
    tmp_file=$(mktemp)
    jq --arg ua "$user_agent" '.user_agent = $ua' "$json_path" > "$tmp_file" && mv "$tmp_file" "$json_path"

    echo -e "\033[1;32m[✓] User-Agent ajouté avec succès.\033[0m"
else
    echo -e "\033[1;31m[!] Fichier $json_path introuvable. Veuillez d’abord créer le profil.\033[0m"
    exit 1
fi
