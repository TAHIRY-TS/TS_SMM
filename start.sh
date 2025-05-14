#!/bin/bash
clear

# Définition des couleurs
ROUGE="\033[0;31m"
JAUNE="\033[0;33m"
CYAN="\033[0;36m"
BLANC="\033[1;37m"
RESET="\033[0m"
BLEU="\033[1;34m"
MAGENTA="\033[1;35m"
VERT="\033[1;32m"

# logo
affichage_logo() {
    source ./assets/logo.sh
}

# Message animé d'accueil
afficher_message_animated() {
    local delay=0.3
    couleurs=(
        "\033[1;31m"  # Rouge
        "\033[1;32m"  # Vert
        "\033[1;33m"  # Jaune
        "\033[1;34m"  # Bleu
        "\033[1;35m"  # Magenta
        "\033[1;36m"  # Cyan
        "\033[1;37m"  # Blanc
    )

    messages=(
        "BUENVIENUE !"
        "WELCOME !"
        "TONGASOA !"
    )

    for texte in "${messages[@]}"; do
        largeur_terminal=$(tput cols)
        longueur=${#texte}
        espace_gauche=$(( (largeur_terminal - longueur) / 2 ))
        printf "%*s" "$espace_gauche" ""
        for ((i=0; i<longueur; i++)); do
            lettre="${texte:$i:1}"
            couleur=${couleurs[$((RANDOM % ${#couleurs[@]}))]}
            echo -ne "${couleur}${lettre}${RESET}"
            sleep 0.1
        done
        echo ""
    done
}

# Fichier de version
VERSION_FILE="assets/version.txt"
VERSION="v1.0"
[[ -f "$VERSION_FILE" ]] && VERSION=$(cat "$VERSION_FILE")

# Fonction pour afficher la version
afficher_version() {
    printf "║        ${CYAN}TS SMM AUTOCLICK - %s${RESET}             ║\n" "$VERSION"
}

# Fonction pour afficher le cadre du menu
afficher_cadre() {
    largeur=55
    titre="MENU PRINCIPAL"
    padding=$(( (largeur - ${#titre} - 2) / 2 ))

    printf "╔"
    printf '═%.0s' $(seq 1 $((largeur - 2)))
    printf "╗\n"

    printf "║"
    printf ' %.0s' $(seq 1 "$padding")
    printf "%s" "$titre"
    printf ' %.0s' $(seq 1 $((largeur - ${#titre} - padding - 2)))
    printf "║\n"

    printf "╠"
    printf '═%.0s' $(seq 1 $((largeur - 2)))
    printf "╣\n"
}

# Afficher les options
afficher_options() {
    echo -e "║ ${VERT}1.${RESET} Se connecter à Telegram                          ║"
    echo -e "║ ${MAGENTA}2.${RESET} Se connetion à Instagram                         ║"
    echo -e "║ ${CYAN}3.${RESET} Lancer l'autoclick SMM                           ║"
    echo -e "║ ${JAUNE}4.${RESET} Lancer une tâche manuellement                    ║"
    echo -e "║ ${VERT}5.${RESET} Mise à jour                                      ║"
    echo -e "║ ${BLEU}10.${RESET} Follow                                          ║"
    echo -e "║ ${BLEU}0.${RESET} Quitter                                          ║"
}

ligne_inferieure() {
    printf "╚"
    printf '═%.0s' $(seq 1 53)
    printf "╝\n"
}
# Fonction principale
menu_principal() {
    affichage_logo
    afficher_message_animated
    afficher_cadre
    afficher_version
    afficher_options
    ligne_inferieure

    echo ""
    echo -ne "${JAUNE}Votre choix : ${RESET}"
    read -r choix

    case $choix in
        1)
            echo -e "${CYAN}Connexion à Telegram...${RESET}"
            termux-open-url "https://my.telegram.org"
            [[ -f scripts/telegram_connect.py ]] && python3 scripts/telegram_connect.py
            ;;

        2)
            echo -e "${CYAN}Gestion de compte Instagram...${RESET}"
            [[ -f scripts/compte_manager.py ]] && python3 scripts/compte_manager.py
            ;;
        3)
            echo -e "${CYAN}Lancement de l'autoclick SMM...${RESET}"
            [[ -f scripts/auto_task_bot.py ]] && python3 scripts/auto_task_bot.py
            ;;
        4)
            echo -e "${CYAN}Lancement d'une tâche manuellement...${RESET}"
            [[ -f scripts/instagram_task.py ]] && python3 scripts/instagram_task.py
            ;;
        5)
            echo -e "${CYAN}Mise à jour...${RESET}"
            [[ -f main/iv.sh ]] && bash main/iv.sh
            ;;
        10)
            echo -e "${CYAN}Attendez...${RESET}"
            [[ -f scripts/auto_follow.py ]] && python3 scripts/auto_follow.py
            ;;
        0)
            echo -e "${BLEU}Fermeture du programme...${RESET}"
            termux-open-url "https://www.facebook.com/profile.php?id=61556805455642"
            cd ~
            exit 0
            ;;
        *)
            echo -e "${ROUGE}Choix invalide, veuillez réessayer.${RESET}"
            ;;
    esac

    echo
    echo -e "${JAUNE}Appuyer sur entrée pour revenir au menu...${RESET}"
    read -r
    clear
    menu_principal
}

# Lancement
menu_principal
