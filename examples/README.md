# Example Configurations

This directory contains example configuration files for different use cases.

## Available Examples

### wasd-config.json
WASD movement configuration with space and ESC keys. Perfect for PC games that use WASD controls.

**Keys mapped:**
- GPIO 17 → W (forward)
- GPIO 27 → A (left)
- GPIO 22 → S (backward)
- GPIO 23 → D (right)
- GPIO 24 → SPACE (jump/action)
- GPIO 25 → ESC (menu)

### gamepad-config.json
Full gamepad-style controller with action buttons and D-pad.

**Keys mapped:**
- GPIO 17 → A button
- GPIO 27 → B button
- GPIO 22 → X button
- GPIO 23 → Y button
- GPIO 24 → UP (D-pad)
- GPIO 25 → DOWN (D-pad)
- GPIO 5 → LEFT (D-pad)
- GPIO 6 → RIGHT (D-pad)
- GPIO 13 → ENTER (start)
- GPIO 19 → ESC (select)

## Using an Example

To use an example configuration:

1. Copy the example to the config location:
```bash
sudo cp examples/wasd-config.json /etc/gpio_keystrokes/config.json
```

2. Restart the service:
```bash
sudo systemctl restart gpio-keystrokes
```

## Creating Your Own

Feel free to use these as templates for your own configurations. Just modify the GPIO pins and key mappings to match your needs.
