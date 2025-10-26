#!/bin/bash

# Noobz Official Bot - Service Installation Script
# This script installs and configures the systemd service

set -e  # Exit on error

echo "=================================================="
echo "🤖 Noobz Official Bot - Service Installation"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root or with sudo${NC}"
    exit 1
fi

# Check if service file exists
if [ ! -f "/root/noobz-bot/official_bot/noobz-official-bot.service" ]; then
    echo -e "${RED}❌ Service file not found!${NC}"
    echo "Expected: /root/noobz-bot/official_bot/noobz-official-bot.service"
    exit 1
fi

# Check if .env file exists
if [ ! -f "/root/noobz-bot/official_bot/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found!${NC}"
    echo "You need to create .env file before starting the bot."
    echo "Copy from .env.example and configure it."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📋 Installation Steps:"
echo ""

# Step 1: Copy service file
echo "1️⃣  Copying service file..."
cp /root/noobz-bot/official_bot/noobz-official-bot.service /etc/systemd/system/
echo -e "${GREEN}✅ Service file copied${NC}"
echo ""

# Step 2: Reload systemd
echo "2️⃣  Reloading systemd daemon..."
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd reloaded${NC}"
echo ""

# Step 3: Enable service
echo "3️⃣  Enabling service (auto-start on boot)..."
systemctl enable noobz-official-bot
echo -e "${GREEN}✅ Service enabled${NC}"
echo ""

# Step 4: Start service
echo "4️⃣  Starting service..."
systemctl start noobz-official-bot
sleep 2
echo -e "${GREEN}✅ Service started${NC}"
echo ""

# Step 5: Check status
echo "5️⃣  Checking service status..."
echo ""
if systemctl is-active --quiet noobz-official-bot; then
    echo -e "${GREEN}✅ Service is running!${NC}"
    echo ""
    systemctl status noobz-official-bot --no-pager -l
else
    echo -e "${RED}❌ Service failed to start!${NC}"
    echo ""
    echo "Showing last 20 log lines:"
    journalctl -u noobz-official-bot -n 20 --no-pager
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=================================================="
echo ""
echo "📝 Useful Commands:"
echo ""
echo "  Check status:    systemctl status noobz-official-bot"
echo "  View logs:       journalctl -u noobz-official-bot -f"
echo "  Restart:         systemctl restart noobz-official-bot"
echo "  Stop:            systemctl stop noobz-official-bot"
echo ""
echo "🔄 Update & Deploy:"
echo ""
echo "  cd /root/noobz-bot"
echo "  git pull origin main"
echo "  systemctl restart noobz-official-bot"
echo ""
echo "=================================================="
