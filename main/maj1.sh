#!/bin/bash

# === CONFIGURATION ===
VERSION_FILE="./assets/version.txt"
VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "Inconnue")
DUREE=2.0  # Durée en secondes par tâche
PAS=5      # Pourcentage de progression à chaque étape
# ======================

# Couleurs
VERT="\033[1;32m"
ROUGE="\033[1;31m"
BLEU="\033[1;34m"
JAUNE="\033[1;33m"
CYAN="\033[1;36m"
RESET="\033[0m"

# Vérification de 'bc'
if ! command -v bc >/dev/null 2>&1; then
  echo -e "${ROUGE}[!] Le paquet 'bc' n'est pas installé. Installation...${RESET}"
  pkg install -y bc
fi

# Horloge
horloge() {
    echo -e "${CYAN}[$(date +'TS %H:%M:%S')]${RESET}"
}

# Barre de progression
progress_bar() {
    local step=$PAS
    local delay=$(echo "$DUREE / (100 / $step)" | bc -l)
    local progress=0

    while [ $progress -le 100 ]; do
        local count=$((progress / 5))
        local bar=$(printf "%-${count}s" | tr ' ' '•')
        printf "\r${BLEU}Progression : [%-20s] %3d%%${RESET}" "$bar" "$progress"
        sleep "$delay"
        progress=$((progress + step))
    done
    echo ""
}

# Entête
clear
echo -e "${MAGENTA}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${RESET}"

echo -e "${MAGENTA}┃  MAJ Automatique   $(horloge) ┃${RESET}"

echo -e "${MAGENTA}┃         ${CYAN}Version $VERSION${RESET}    ┃${RESET}"

echo -e "${MAGENTA}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${RESET}"

echo -e "${JAUNE}[1] Mitahiry ireo doné rehetra...${RESET}"
progress_bar && git stash > /dev/null

echo -e "${JAUNE}[2] Telechargement...${RESET}"
progress_bar && git pull > /dev/null

echo -e "${JAUNE}[3] Mamemerina ilay donné rehetra...${RESET}"
progress_bar && git stash pop > /dev/null

echo -e "\n${VERT}✓ Vita tsara ! Version ampiasaina : $VERSION${RESET}\n"

# Demande de sortie
echo -e "${JAUNE}Tsara kokoa mivoaka kely mba hampiharana ilay mise à jour ?${RESET}"
echo -e "${CYAN}[1] Eny, miala Termux${RESET}"
echo -e "${CYAN}[2] Tsia, hijanona eto${RESET}"
read -p "$(horloge) Choix: " reponse

case $reponse in
    1)
        echo -e "${VERT}Fivoahana..., miverina ianao avy eo.${RESET}"
        sleep 2
        cd ~
        cd TS-smm
        ;;
    2)
        echo -e "${JAUNE}Okay, nisafidy hijanona ato amin'ny Termux ianao.${RESET}"
        bash start.sh
        ;;
    *)
        echo -e "${ROUGE}Safidy tsy mety. Hijanona ato izany.${RESET}"
        ;;
esac
