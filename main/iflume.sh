#!/bin/bash

# === CONFIGURATION ===
CONFIG_DIR="$HOME/.ts_secure"
KEY_FILE="$CONFIG_DIR/key.txt"
EXPIRY_FILE="$CONFIG_DIR/expiry.txt"
VALID_KEY="TAHIRY-TS-123456"
LOGO_FILE="assets/logo.sh"

# === COULEURS ===
RED='\e[1;31m'
GREEN='\e[1;32m'
YELLOW='\e[1;33m'
CYAN='\e[1;36m'
NC='\e[0m' # No Color

# === INITIALISATION ===
init_config() {
  mkdir -p "$CONFIG_DIR"
}

show_logo() {
  if [ -f "$LOGO_FILE" ]; then
    bash "$LOGO_FILE"
  else
    echo -e "${YELLOW}[!] Logo non trouvé dans $LOGO_FILE${NC}"
  fi
}

# === VÉRIFICATION DE CLÉ ===
check_key() {
  if [ ! -f "$KEY_FILE" ]; then
    echo -e "${CYAN}>>> Veuillez entrer votre clé d'activation :${NC}"
    read -p "Clé : " user_key

    if [ "$user_key" = "$VALID_KEY" ]; then
      echo "$user_key" > "$KEY_FILE"
      date -d "+1 day" +%s > "$EXPIRY_FILE"
      echo -e "${GREEN}[✓] Clé activée avec succès pour 24h.${NC}"
    else
      echo -e "${RED}[✗] Clé invalide. Contacte l’administrateur.${NC}"
      exit 1
    fi
  fi
}

# === VÉRIFICATION D’EXPIRATION ===
check_expiry() {
  now=$(date +%s)
  expiry=$(cat "$EXPIRY_FILE")
  if [ "$now" -gt "$expiry" ]; then
    echo -e "${RED}[✗] Votre accès a expiré.${NC}"
    rm -f "$KEY_FILE" "$EXPIRY_FILE"
    exit 1
  fi
}

# === MENU PRINCIPAL ===
run_main() {
  clear
  show_logo
  echo -e "${GREEN}Bienvenue dans l'interface sécurisée TAHIRY TS.${NC}"
  echo ""
  echo -e "${YELLOW}Chargement de vos outils...${NC}"
  # Place ici tes outils / actions
}
# -- nouvelle fonction --
check_online_key() {
  CHAT_ID=$(curl -s https://tonserveur.com/serve_keys.php?secret=MON_SECRET_SERVEUR \
    | jq -r --arg id "$TELEGRAM_ID" '.[$id].expires_at // empty')
  if [ -z "$CHAT_ID" ]; then
    echo -e "${RED}[✗] Aucune activation détectée pour ton compte Telegram.${NC}"
    exit 1
  fi
  now=$(date +%s)
  if [ "$now" -gt "$CHAT_ID" ]; then
    echo -e "${RED}[✗] Ton abonnement Telegram est expiré.${NC}"
    exit 1
  fi
}

# === EXECUTION ===
init_config
check_online_key
check_key
check_expiry
run_main
