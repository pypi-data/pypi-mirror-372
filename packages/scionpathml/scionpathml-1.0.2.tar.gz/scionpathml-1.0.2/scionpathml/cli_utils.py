#Utility functions for command-line interface styling and helpers
import os
import subprocess
import importlib.util
import ipaddress
import re
from datetime import datetime

# Color codes for better visual output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE} {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def print_example(command, description):
    """Print command example"""
    print(f"{Colors.MAGENTA}  Example:{Colors.END} {Colors.BOLD}{command}{Colors.END}")
    print(f"           {description}")

def print_section(title):
    """Print a section title"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")

def validate_ip_address(ip_str):
    """Validate if the provided string is a valid IPv4 address."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return isinstance(ip, ipaddress.IPv4Address)
    except ValueError:
        return False

def validate_as_id(as_id):
    """Validate AS ID format according to SCION specifications."""
    pattern = r'^\d+-ffaa:[0-9a-fA-F]+:[0-9a-fA-F]+$'
    return re.match(pattern, as_id) is not None

def validate_as_name(name):
    """Validate AS/Server name format."""
    if not name or len(name) > 50:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, name) is not None

def validate_inputs(as_id=None, ip=None, name=None):
    """Validate multiple inputs and return detailed error messages."""
    errors = []
    if as_id is not None and not validate_as_id(as_id):
        errors.append(f"Invalid AS ID format: '{as_id}'")
        errors.append("  Expected format: 'number-ffaa:hex:hex' (e.g., 19-ffaa:1:11de)")
        
    if ip is not None and not validate_ip_address(ip):
        errors.append(f"Invalid IPv4 address: '{ip}'")
        errors.append("  Please provide a valid IPv4 address (e.g., 192.168.1.100)")
        
    if name is not None and not validate_as_name(name):
        errors.append(f"Invalid name: '{name}'")
        errors.append("  Name rules: alphanumeric + hyphens/underscores, max 50 chars")
        errors.append("  Valid examples: 'AS-Server-1', 'test_server', 'MyAS123'")
        
    return errors

def load_config(config_file="./collector/config.py"):
    """Load configuration from config.py file"""
    try:
        spec = importlib.util.spec_from_file_location("config", config_file)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config
    except FileNotFoundError:
        print_error(f"Configuration file not found: {config_file}")
        print_info("Make sure you're running this from the correct directory")
        return None
    except Exception as e:
        print_error(f"Error loading configuration: {e}")
        return None

def update_config_section(config_file, section, key, value, remove=False, silent=False):
    """Update configuration file sections."""
    try:
        with open(config_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print_error(f"Configuration file not found: {config_file}")
        return False
    
    new_lines = []
    in_section = False
    updated = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(section + " = {"):
            in_section = True
            new_lines.append(line)
            continue
            
        if in_section:
            if stripped == "}":
                if not remove and not updated:
                    new_lines.append(f'    "{key}": {value},\n')
                    updated = True
                in_section = False
                new_lines.append(line)
                continue
                
            if stripped.startswith(f'"{key}"'):
                if remove:
                    updated = True
                    continue
                else:
                    new_lines.append(f'    "{key}": {value},\n')
                    updated = True
                    continue
                    
        new_lines.append(line)
    
    if not silent and remove and not updated:
        print_error(f"Key '{key}' not found in section {section}. Nothing was removed.")
        return False
    
    with open(config_file, "w") as f:
        f.writelines(new_lines)
    
    return True