#!/bin/bash

# GTA-RP Bot Setup Script for Strato VPS (Ubuntu/Debian)
# Dieses Skript installiert alle Abhängigkeiten und richtet den Bot als Hintergrunddienst ein.

echo "🚀 Starte Bot-Setup auf deinem Strato VPS..."

# 1. System-Updates
sudo apt update && sudo apt upgrade -y

# 2. Python & Abhängigkeiten installieren
sudo apt install -y python3 python3-pip python3-venv git screen nginx curl

# 3. Virtuelle Umgebung erstellen
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtuelle Umgebung erstellt."
fi

# 4. Python-Module installieren
source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install discord.py streamlit pillow
fi

# 5. Systemd Service für den Bot erstellen
echo "⚙️ Erstelle Hintergrund-Dienste..."

USER_NAME=$(whoami)
REPO_PATH=$(pwd)

sudo bash -c "cat > /etc/systemd/system/discord-bot.service <<EOF
[Unit]
Description=Discord Bot für GTA RP
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$REPO_PATH
ExecStart=$REPO_PATH/venv/bin/python3 $REPO_PATH/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# 6. Systemd Service für das Dashboard erstellen
sudo bash -c "cat > /etc/systemd/system/discord-dashboard.service <<EOF
[Unit]
Description=Streamlit Dashboard für Discord Bot
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$REPO_PATH
ExecStart=$REPO_PATH/venv/bin/python3 -m streamlit run $REPO_PATH/dashboard.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# 7. Dienste aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl enable discord-dashboard
sudo systemctl start discord-bot
sudo systemctl start discord-dashboard

echo "--------------------------------------------------"
echo "✅ Setup abgeschlossen!"
echo "🤖 Bot-Status prüfen: sudo systemctl status discord-bot"
echo "📊 Dashboard-Status prüfen: sudo systemctl status discord-dashboard"
echo "🌐 Dashboard erreichbar unter: http://$(curl -s ifconfig.me):8501"
echo "--------------------------------------------------"
