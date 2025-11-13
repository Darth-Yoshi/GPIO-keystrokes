#!/usr/bin/env python3
"""
GPIO to Keystroke Converter
Monitors GPIO pins and emulates keyboard presses for Raspberry Pi
"""

import json
import os
import sys
import signal
import logging
from pathlib import Path

try:
    import RPi.GPIO as GPIO
    import uinput
except ImportError as e:
    print(f"Error: {e}")
    print("This program requires RPi.GPIO and python-uinput libraries.")
    print("Install with: sudo apt-get install python3-rpi.gpio python3-uinput")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Key mappings from config string to uinput key codes
KEY_MAP = {
    'UP': uinput.KEY_UP,
    'DOWN': uinput.KEY_DOWN,
    'LEFT': uinput.KEY_LEFT,
    'RIGHT': uinput.KEY_RIGHT,
    'SPACE': uinput.KEY_SPACE,
    'ESC': uinput.KEY_ESC,
    '1': uinput.KEY_1,
    '2': uinput.KEY_2,
    '3': uinput.KEY_3,
    'ENTER': uinput.KEY_ENTER,
    'A': uinput.KEY_A,
    'B': uinput.KEY_B,
    'C': uinput.KEY_C,
    'D': uinput.KEY_D,
    'E': uinput.KEY_E,
    'F': uinput.KEY_F,
    'G': uinput.KEY_G,
    'H': uinput.KEY_H,
    'I': uinput.KEY_I,
    'J': uinput.KEY_J,
    'K': uinput.KEY_K,
    'L': uinput.KEY_L,
    'M': uinput.KEY_M,
    'N': uinput.KEY_N,
    'O': uinput.KEY_O,
    'P': uinput.KEY_P,
    'Q': uinput.KEY_Q,
    'R': uinput.KEY_R,
    'S': uinput.KEY_S,
    'T': uinput.KEY_T,
    'U': uinput.KEY_U,
    'V': uinput.KEY_V,
    'W': uinput.KEY_W,
    'X': uinput.KEY_X,
    'Y': uinput.KEY_Y,
    'Z': uinput.KEY_Z,
}


class GPIOKeystrokeConverter:
    """Converts GPIO button presses to keyboard events"""
    
    def __init__(self, config_path):
        """Initialize the converter with a configuration file"""
        self.config_path = config_path
        self.config = self.load_config()
        self.device = None
        self.running = False
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)
            
    def setup_gpio(self):
        """Setup GPIO pins based on configuration"""
        GPIO.setmode(GPIO.BCM)
        
        # Get bounce time from config, default to 200ms
        bounce_time = self.config.get('bounce_time_ms', 200)
        
        for pin_config in self.config['buttons']:
            pin = pin_config['gpio_pin']
            pull_up_down = GPIO.PUD_UP if pin_config.get('pull_up', True) else GPIO.PUD_DOWN
            
            GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
            
            # Setup event detection
            # If pull_up is True, button press pulls pin LOW (falling edge)
            # If pull_up is False, button press pulls pin HIGH (rising edge)
            edge = GPIO.FALLING if pin_config.get('pull_up', True) else GPIO.RISING
            
            GPIO.add_event_detect(
                pin, 
                edge, 
                callback=self.button_callback, 
                bouncetime=bounce_time
            )
            
            logger.info(f"Setup GPIO pin {pin} for key '{pin_config['key']}'")
    
    def button_callback(self, pin):
        """Callback function when a button is pressed"""
        # Find which key this pin is mapped to
        for pin_config in self.config['buttons']:
            if pin_config['gpio_pin'] == pin:
                key_name = pin_config['key']
                if key_name in KEY_MAP:
                    key_code = KEY_MAP[key_name]
                    logger.info(f"Button press on GPIO {pin} -> Key '{key_name}'")
                    self.emit_key(key_code)
                else:
                    logger.warning(f"Unknown key mapping: {key_name}")
                break
    
    def emit_key(self, key_code):
        """Emit a keyboard press event"""
        if self.device:
            self.device.emit_click(key_code)
    
    def setup_uinput(self):
        """Setup uinput virtual keyboard device"""
        # Collect all key codes from the configuration
        key_codes = []
        for pin_config in self.config['buttons']:
            key_name = pin_config['key']
            if key_name in KEY_MAP:
                key_codes.append(KEY_MAP[key_name])
        
        # Create virtual keyboard device
        self.device = uinput.Device(key_codes)
        logger.info("Virtual keyboard device created")
    
    def run(self):
        """Start the GPIO to keystroke converter"""
        logger.info("Starting GPIO Keystroke Converter")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            self.setup_uinput()
            self.setup_gpio()
            
            self.running = True
            logger.info("GPIO Keystroke Converter is running. Press Ctrl+C to exit.")
            
            # Keep the program running
            signal.pause()
            
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            self.cleanup()
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup GPIO and uinput resources"""
        logger.info("Cleaning up resources")
        self.running = False
        
        if self.device:
            self.device.destroy()
            
        GPIO.cleanup()
        logger.info("Cleanup complete")


def main():
    """Main entry point"""
    # Default config path
    default_config = '/etc/gpio_keystrokes/config.json'
    
    # Check for config file in multiple locations
    config_paths = [
        os.path.expanduser('~/.config/gpio_keystrokes/config.json'),
        './config.json',
        default_config
    ]
    
    config_path = None
    for path in config_paths:
        if os.path.exists(path):
            config_path = path
            break
    
    if not config_path:
        logger.error("No configuration file found. Searched locations:")
        for path in config_paths:
            logger.error(f"  - {path}")
        logger.error("Please create a configuration file.")
        sys.exit(1)
    
    converter = GPIOKeystrokeConverter(config_path)
    converter.run()


if __name__ == '__main__':
    main()
