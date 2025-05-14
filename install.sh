#!/bin/bash

# Couleurs
cyan='\033[1;36m'
yellow='\033[1;33m'
green='\033[1;32m'
red='\033[1;31m'
reset='\033[0m'

horloge() {
    echo -ne "${cyan}[TS $(date +%H:%M)]${reset} "
}

clear
horloge; echo -e "${yellow}Installation des dépendances Termux...${reset}"

# Mise à jour des paquets
pkg update -y && pkg upgrade -y
pkg install python rust clang libffi openssl git -y

# Mise à jour de pip
pip install --upgrade pip setuptools wheel
pip install instagram_private_api
# Fichier requirements.txt par défaut
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt <<EOF
cryptography==41.0.4
telethon>=1.33.1
requests>=2.31.0
beautifulsoup4>=4.12.3
instagrapi<2.0
colorama
EOF
fi

# Installation via pip
horloge; echo -e "${green}Installation via requirements.txt...${reset}"
pkg install -r requirements.txt

# Création des dossiers
horloge; echo -e "${green}Création des dossiers nécessaires...${reset}"
mkdir -p config scripts assets accounts
chmod +x *.sh

# Lancer le script de mise à jour automatique si non lancé
if ! pgrep -f "maj1.sh" > /dev/null; then
    horloge; echo -e "${yellow}Lancement du vérificateur de mise à jour...${reset}"
    nohup bash main/maj1.sh> /dev/null 2>&1 &
fi

# Affichage du logo
if [ -f assets/logo.sh ]; then
    bash assets/logo.sh
    sleep 3
    clear
fi

horloge; echo -e "${green}Installation terminée.${reset}"
echo 'bash ~/TS-smm/main/maj1.sh' >> ~/.bashrc
# Lancement du script principal
chmod +x *.sh
if [ -f start.sh ]; then
    horloge; echo -e "${yellow}Lancement de l'application...${reset}"
    bash start.sh
else
    horloge; echo -e "${red}Erreur : script de demarrage introuvable.${reset}"
fi
