# GPIO Keystrokes

A background service for Raspberry Pi that converts GPIO physical button presses to keyboard keystrokes. Perfect for building custom controllers, arcade machines, or any project requiring button input to be translated into keyboard events.

## Features

- 🎮 Maps GPIO pins to keyboard keys
- ⚙️ Fully configurable via JSON config file
- 🔄 Runs as a systemd background service
- 🎯 Debouncing support to prevent multiple triggers
- 📝 Comprehensive logging
- 🔌 Supports pull-up and pull-down resistor configurations

## Default Key Mappings

The default configuration includes mappings for:
- **Arrow Keys** (UP, DOWN, LEFT, RIGHT)
- **Spacebar**
- **Number Keys** (1, 2, 3)
- **ESC** key

## Hardware Setup

### Wiring

For the default configuration, connect buttons between the following GPIO pins and Ground (assuming pull-up resistors, which is the default):

| GPIO Pin (BCM) | Key    | Physical Pin |
|----------------|--------|--------------|
| 17             | UP     | 11           |
| 27             | DOWN   | 13           |
| 22             | LEFT   | 15           |
| 23             | RIGHT  | 16           |
| 24             | SPACE  | 18           |
| 25             | 1      | 22           |
| 5              | 2      | 29           |
| 6              | 3      | 31           |
| 13             | ESC    | 33           |

**Note**: Connect one side of each button to the GPIO pin and the other side to Ground (GND). The internal pull-up resistor is enabled by default.

## Installation

### Prerequisites

- Raspberry Pi (any model with GPIO pins)
- Raspbian/Raspberry Pi OS
- Root/sudo access

### Quick Install

1. Clone this repository:
```bash
git clone https://github.com/Darth-Yoshi/GPIO-keystrokes.git
cd GPIO-keystrokes
```

2. Run the installation script:
```bash
sudo ./install.sh
```

3. Start the service:
```bash
sudo systemctl start gpio-keystrokes
```

4. Enable on boot (optional):
```bash
sudo systemctl enable gpio-keystrokes
```

### Manual Installation

If you prefer to install manually:

1. Install dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-rpi.gpio
sudo pip3 install -r requirements.txt
```

2. Load the uinput kernel module:
```bash
sudo modprobe uinput
echo "uinput" | sudo tee -a /etc/modules
```

3. Copy files:
```bash
sudo cp gpio_keystrokes.py /usr/local/bin/
sudo chmod +x /usr/local/bin/gpio_keystrokes.py
sudo mkdir -p /etc/gpio_keystrokes
sudo cp config.json /etc/gpio_keystrokes/
sudo cp gpio-keystrokes.service /etc/systemd/system/
```

4. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gpio-keystrokes
sudo systemctl start gpio-keystrokes
```

## Configuration

The configuration file is located at `/etc/gpio_keystrokes/config.json`. You can customize the button mappings by editing this file.

### Configuration Format

```json
{
  "bounce_time_ms": 200,
  "buttons": [
    {
      "gpio_pin": 17,
      "key": "UP",
      "pull_up": true
    }
  ]
}
```

### Configuration Parameters

- **bounce_time_ms**: Debounce time in milliseconds (prevents multiple triggers from a single button press)
- **buttons**: Array of button configurations
  - **gpio_pin**: GPIO pin number (BCM numbering)
  - **key**: Key to emit (see supported keys below)
  - **pull_up**: Set to `true` for pull-up resistor (button connects to GND), `false` for pull-down (button connects to 3.3V)

### Supported Keys

The following keys are supported in the configuration:

**Arrow Keys**: `UP`, `DOWN`, `LEFT`, `RIGHT`

**Special Keys**: `SPACE`, `ENTER`, `ESC`

**Number Keys**: `1`, `2`, `3`

**Letter Keys**: `A` through `Z`

### Example: Custom Configuration

To create a custom 4-button controller:

```json
{
  "bounce_time_ms": 150,
  "buttons": [
    {
      "gpio_pin": 17,
      "key": "W",
      "pull_up": true
    },
    {
      "gpio_pin": 27,
      "key": "A",
      "pull_up": true
    },
    {
      "gpio_pin": 22,
      "key": "S",
      "pull_up": true
    },
    {
      "gpio_pin": 23,
      "key": "D",
      "pull_up": true
    }
  ]
}
```

After editing the configuration, restart the service:
```bash
sudo systemctl restart gpio-keystrokes
```

## Usage

### Service Management

Start the service:
```bash
sudo systemctl start gpio-keystrokes
```

Stop the service:
```bash
sudo systemctl stop gpio-keystrokes
```

Restart the service:
```bash
sudo systemctl restart gpio-keystrokes
```

Check status:
```bash
sudo systemctl status gpio-keystrokes
```

View logs:
```bash
sudo journalctl -u gpio-keystrokes -f
```

### Running Manually (for testing)

You can run the script manually for testing:

```bash
sudo python3 gpio_keystrokes.py
```

Press Ctrl+C to stop.

## Troubleshooting

### Service won't start

1. Check the logs:
```bash
sudo journalctl -u gpio-keystrokes -xe
```

2. Verify uinput module is loaded:
```bash
lsmod | grep uinput
```

If not loaded:
```bash
sudo modprobe uinput
```

### Buttons not responding

1. Test GPIO pins with a simple script to verify hardware connection
2. Check the configuration file for correct GPIO pin numbers
3. Verify you're using BCM pin numbering (not physical pin numbers)
4. Check the pull-up/pull-down configuration matches your wiring

### Permission errors

The service needs root access to interact with GPIO and uinput. Make sure:
- The service is configured to run as root (default in the service file)
- The uinput module is loaded
- Your user is in the `input` group (if running manually): `sudo usermod -a -G input $USER`

## Uninstallation

To remove the service:

```bash
sudo systemctl stop gpio-keystrokes
sudo systemctl disable gpio-keystrokes
sudo rm /etc/systemd/system/gpio-keystrokes.service
sudo rm /usr/local/bin/gpio_keystrokes.py
sudo rm -rf /etc/gpio_keystrokes
sudo systemctl daemon-reload
```

## License

MIT License - Feel free to use and modify for your projects!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.