#!/bin/bash
clear

# === Couleurs ===
RESET="\033[0m"
ROUGE="\033[1;31m"
VERT="\033[1;32m"
JAUNE="\033[1;33m"
CYAN="\033[1;36m"

# Définir l'URL du dépôt Git (si besoin plus tard)
DEPOT_URL="https://github.com/TAHIRYAndriatefy/TS-smm.git"
# allignement
centrer() {
  local text="$1"
  local term_width=$(tput cols)
  local text_length=${#text}
  local padding=$(( (term_width - text_length) / 2 ))
  printf "%*s%s\n" "$padding" "" "$text"
}
# Fonction Horloge
horloge() {
    echo -e "${CYAN}[TS $(date +'%H:%M')]${RESET}"
}

# logo
afficher_logo() {
    if [[ -f assets/logo.sh ]]; then
        bash assets/logo.sh
    else
        echo -e "\033[1;31m[!] Logo introuvable dans assets/logo.sh\033[0m"
    fi
}
# Message animé d'accueil
animated() {
    local msg="     MISAOTRA ANAO MAMPIASA, AZA MISALASALA MANONTANY 
                  RAHA MISY TSY AZO"
    local delay=0.03
    for ((i=0; i<${#msg}; i++)); do
        echo -ne "${msg:$i:1}"
        sleep $delay
    done
    echo ""
}

# Menu principal de mise à jour
menu() {
    clear
    afficher_logo
    animated
      centrer "╔════════════════════════════════════╗"
      centrer "║        MENU DE MISE À JOUR         ║"
      centrer "╚════════════════════════════════════╝"
    
    echo -e "${JAUNE}1.${RESET} Mise à jour du projet"
    echo -e "${JAUNE}2.${RESET} Autre action"
    echo -e "${JAUNE}3.${RESET} Quitter"
    echo ""
    echo -ne "$(horloge)${VERT}Choix:${RESET} "
    read -r choix

    case $choix in
        1)
            bash scripts/maj1.sh
            ;;
        2)
            echo -e "$(horloge)${CYAN}Autre action à définir...${RESET}"
            echo -e "${JAUNE}Appuyez sur Entrée pour revenir au menu...${RESET}"
            read -r
            menu
            ;;
        3)
            echo -e "$(horloge)${VERT}Merci d'avoir utilisé le script. À bientôt !${RESET}"
            sleep 2
            exit 0  # <- quitte proprement le script/Termux si seul onglet
            ;;
        *)
            echo -e "${ROUGE}Choix invalide. Veuillez réessayer.${RESET}"
            sleep 1
            menu
            ;;
    esac
}

# Lancement
menu
