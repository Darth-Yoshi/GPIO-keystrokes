#!/bin/bash
# Installation script for GPIO Keystroke Converter

set -e

echo "Installing GPIO Keystroke Converter..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-pip python3-rpi.gpio

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Load uinput kernel module
echo "Loading uinput kernel module..."
modprobe uinput

# Make uinput load on boot
if ! grep -q "uinput" /etc/modules; then
    echo "uinput" >> /etc/modules
    echo "Added uinput to /etc/modules"
fi

# Create config directory
echo "Creating configuration directory..."
mkdir -p /etc/gpio_keystrokes

# Copy configuration file
if [ ! -f /etc/gpio_keystrokes/config.json ]; then
    cp config.json /etc/gpio_keystrokes/config.json
    echo "Installed default configuration to /etc/gpio_keystrokes/config.json"
else
    echo "Configuration file already exists at /etc/gpio_keystrokes/config.json"
fi

# Copy main script
echo "Installing main script..."
cp gpio_keystrokes.py /usr/local/bin/gpio_keystrokes.py
chmod +x /usr/local/bin/gpio_keystrokes.py

# Install systemd service
echo "Installing systemd service..."
cp gpio-keystrokes.service /etc/systemd/system/gpio-keystrokes.service
systemctl daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "To start the service now:"
echo "  sudo systemctl start gpio-keystrokes"
echo ""
echo "To enable the service to start on boot:"
echo "  sudo systemctl enable gpio-keystrokes"
echo ""
echo "To check the status:"
echo "  sudo systemctl status gpio-keystrokes"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u gpio-keystrokes -f"
echo ""
echo "Configuration file: /etc/gpio_keystrokes/config.json"
