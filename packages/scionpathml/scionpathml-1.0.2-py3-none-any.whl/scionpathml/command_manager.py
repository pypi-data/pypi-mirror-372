#Manages pipeline command enabling/disabling and categories
"""
Command Management for SCIONPATHML
Handles enabling/disabling of different pipeline commands
"""

import os
import re
import subprocess
from typing import Dict, List, Tuple, Optional

try:
    from scionpathml import Colors, print_header, print_success, print_error, print_warning, print_info, print_section, print_example, load_config, CONFIG_FILE
except ImportError:

    class Colors:
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        BOLD = '\033[1m'
        END = '\033[0m'
    
    CONFIG_FILE = "./collector/config.py"
    
    def print_header(text): print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n {text}\n{'='*60}{Colors.END}")
    def print_success(text): print(f"{Colors.GREEN}[SUCCESS] {text}{Colors.END}")
    def print_error(text): print(f"{Colors.RED}[ERROR] {text}{Colors.END}")
    def print_warning(text): print(f"{Colors.YELLOW}[WARNING] {text}{Colors.END}")
    def print_info(text): print(f"{Colors.CYAN}[INFO] {text}{Colors.END}")
    def print_section(title): print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
    def print_example(command, description): print(f"{Colors.MAGENTA}  Example:{Colors.END} {Colors.BOLD}{command}{Colors.END}\n           {description}")

def get_default_pipeline_commands() -> Dict:
    """
    Get the default pipeline commands configuration.
    
    Returns:
        Dict: Default pipeline commands configuration
    """
    return {
        "pathdiscovery": {
            "enabled": True,
            "script": "pathdiscovery.py",
            "description": "Discover available network paths using SCION",
            "category": "discovery",
            "execution_order": 1
        },
        "comparer": {
            "enabled": True,
            "script": "comparer.py", 
            "description": "Compare and analyze discovered paths",
            "category": "analysis",
            "execution_order": 2
        },
        "prober": {
            "enabled": True,
            "script": "prober.py",
            "description": "Basic network connectivity probing",
            "category": "probing",
            "execution_order": 3
        },
        "mp-prober": {
            "enabled": True,
            "script": "mp-prober.py",
            "description": "Multi-path network probing",
            "category": "probing",
            "execution_order": 4
        },
        "traceroute": {
            "enabled": True,
            "script": "traceroute.py",
            "description": "Collect traceroute information",
            "category": "tracing",
            "execution_order": 5
        },
        "bandwidth": {
            "enabled": True,
            "script": "bandwidth.py",
            "description": "Measure bandwidth for all discovered paths",
            "category": "bandwidth",
            "execution_order": 6
        },
        "mp-bandwidth": {
            "enabled": True,
            "script": "mp-bandwidth.py",
            "description": "Multi-path bandwidth measurement",
            "category": "bandwidth",
            "execution_order": 7
        }
    }

def ensure_pipeline_commands_in_config() -> bool:
    """
    Ensure PIPELINE_COMMANDS section exists in config.py
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(CONFIG_FILE):
        print_error(f"Configuration file not found: {CONFIG_FILE}")
        return False
    
    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read()
        
        # Check if PIPELINE_COMMANDS already exists
        if "PIPELINE_COMMANDS" in content:
            return True
        
        # Add PIPELINE_COMMANDS section
        default_commands = get_default_pipeline_commands()
        commands_str = "# Pipeline commands configuration\nPIPELINE_COMMANDS = {\n"
        
        for cmd_name, config in default_commands.items():
            commands_str += f'    "{cmd_name}": {{\n'
            commands_str += f'        "enabled": {config["enabled"]},\n'
            commands_str += f'        "script": "{config["script"]}",\n'
            commands_str += f'        "description": "{config["description"]}",\n'
            commands_str += f'        "category": "{config["category"]}",\n'
            commands_str += f'        "execution_order": {config["execution_order"]}\n'
            commands_str += '    },\n'
        
        commands_str += "}\n\n"
        
        # Append to config file
        with open(CONFIG_FILE, "a") as f:
            f.write("\n" + commands_str)
        
        print_success("Added PIPELINE_COMMANDS configuration to config.py")
        return True
        
    except Exception as e:
        print_error(f"Error updating configuration: {e}")
        return False

def load_command_config():
    """Load command configuration, creating it if it doesn't exist"""
    try:
        # First ensure the config has PIPELINE_COMMANDS
        if not ensure_pipeline_commands_in_config():
            return None
            
        # Now load the config
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config
    except Exception as e:
        print_error(f"Error loading command configuration: {e}")
        return None

def show_pipeline_commands():
    """Display current pipeline commands configuration"""
    print_header("PIPELINE COMMANDS CONFIGURATION")
    
    config = load_command_config()
    if not config:
        return
    
    if not hasattr(config, 'PIPELINE_COMMANDS'):
        print_error("PIPELINE_COMMANDS not found in configuration")
        print_info("Run this command again to auto-create the configuration")
        return
    
    # Group commands by category and sort by execution order
    categories = {}
    for cmd_name, cmd_config in config.PIPELINE_COMMANDS.items():
        category = cmd_config.get('category', 'other')
        if category not in categories:
            categories[category] = []
        categories[category].append((cmd_name, cmd_config))
    
    # Sort commands within each category by execution order
    for category in categories:
        categories[category].sort(key=lambda x: x[1].get('execution_order', 999))
    
    # Display by category
    for category, commands in categories.items():
        print_section(f"{category.upper()} COMMANDS")
        
        for cmd_name, cmd_config in commands:
            status = f"{Colors.GREEN}[ENABLED]{Colors.END}" if cmd_config.get('enabled', False) else f"{Colors.RED}[DISABLED]{Colors.END}"
            order = cmd_config.get('execution_order', '?')
            print(f"  {Colors.BOLD}[{order}] {cmd_name}{Colors.END}")
            print(f"    • Status: {status}")
            print(f"    • Script: {Colors.CYAN}{cmd_config.get('script', 'N/A')}{Colors.END}")
            print(f"    • Description: {cmd_config.get('description', 'No description')}")
            print()
    
    # Count enabled/disabled
    enabled_count = sum(1 for cmd in config.PIPELINE_COMMANDS.values() if cmd.get('enabled', False))
    total_count = len(config.PIPELINE_COMMANDS)
    
    print_section("EXECUTION SUMMARY")
    print(f"  • Enabled commands: {Colors.BOLD}{Colors.GREEN}{enabled_count}{Colors.END}")
    print(f"  • Disabled commands: {Colors.BOLD}{Colors.RED}{total_count - enabled_count}{Colors.END}")
    print(f"  • Total commands: {Colors.BOLD}{total_count}{Colors.END}")
    
    if enabled_count > 0:
        # Show execution order of enabled commands
        enabled_commands = [
            (name, config.get('execution_order', 999)) 
            for name, config in config.PIPELINE_COMMANDS.items() 
            if config.get('enabled', False)
        ]
        enabled_commands.sort(key=lambda x: x[1])
        
        print(f"\n  Execution Order:")
        for i, (cmd_name, order) in enumerate(enabled_commands, 1):
            print(f"    {i}. {cmd_name}")
    
    print()
    print_info("Command Management:")
    print_example("scionpathml enable-cmd -m bandwidth", "Enable bandwidth command")
    print_example("scionpathml disable-cmd -m traceroute", "Disable traceroute command")
    print_example("scionpathml enable-category -c bandwidth", "Enable all bandwidth commands")
    print_example("scionpathml disable-category -c probing", "Disable all probing commands")

def get_available_command_names() -> List[str]:
    """Get list of available command names"""
    config = load_command_config()
    if not config or not hasattr(config, 'PIPELINE_COMMANDS'):
        return []
    return list(config.PIPELINE_COMMANDS.keys())

def get_available_categories() -> List[str]:
    """Get list of available command categories"""
    config = load_command_config()
    if not config or not hasattr(config, 'PIPELINE_COMMANDS'):
        return []
    
    categories = set()
    for cmd_config in config.PIPELINE_COMMANDS.values():
        categories.add(cmd_config.get('category', 'other'))
    return sorted(list(categories))

def validate_command_name(cmd_name: str) -> bool:
    """
    Validate if command name exists
    
    Args:
        cmd_name (str): Command name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    available_commands = get_available_command_names()
    return cmd_name in available_commands

def update_pipeline_command(cmd_name: str, enabled: bool) -> bool:
    """
    Update pipeline command enabled status
    
    Args:
        cmd_name (str): Name of the command
        enabled (bool): Whether to enable or disable
        
    Returns:
        bool: True if successful, False otherwise
    """
    config = load_command_config()
    if not config:
        return False
    
    if not hasattr(config, 'PIPELINE_COMMANDS'):
        print_error("PIPELINE_COMMANDS not found in configuration")
        return False
    
    if not validate_command_name(cmd_name):
        print_error(f"Command '{cmd_name}' not found")
        print_info("Available commands:")
        for name in get_available_command_names():
            print(f"  • {name}")
        return False
    
    # Read config file
    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print_error(f"Configuration file not found: {CONFIG_FILE}")
        return False
    
    # Update the specific command
    pattern = rf'("{cmd_name}": \{{[^}}]*"enabled": )(True|False)'
    replacement = rf'\g<1>{str(enabled)}'
    new_content = re.sub(pattern, replacement, content)
    
    if content == new_content:
        status = "enabled" if enabled else "disabled"
        print_warning(f"Command '{cmd_name}' is already {status}")
        return True
    
    # Write back to file
    with open(CONFIG_FILE, "w") as f:
        f.write(new_content)
    
    status = "enabled" if enabled else "disabled"
    print_success(f"Command '{cmd_name}' {status} successfully!")
    
    # Show impact
    config = load_command_config()
    if config and hasattr(config, 'PIPELINE_COMMANDS'):
        enabled_count = sum(1 for cmd in config.PIPELINE_COMMANDS.values() if cmd.get('enabled', False))
        print_info(f"Pipeline will now execute {enabled_count} commands")
    
    return True

def enable_commands_by_category(category: str) -> bool:
    """
    Enable all commands in a specific category
    
    Args:
        category (str): Category name
        
    Returns:
        bool: True if successful, False otherwise
    """
    print_header(f"ENABLING ALL {category.upper()} COMMANDS")
    
    config = load_command_config()
    if not config or not hasattr(config, 'PIPELINE_COMMANDS'):
        return False
    
    # Find commands in category
    commands_in_category = [
        cmd_name for cmd_name, cmd_config in config.PIPELINE_COMMANDS.items()
        if cmd_config.get('category', 'other') == category
    ]
    
    if not commands_in_category:
        print_error(f"No commands found in category '{category}'")
        print_info("Available categories:")
        for cat in get_available_categories():
            print(f"  • {cat}")
        return False
    
    print_info(f"Found {len(commands_in_category)} commands in '{category}' category:")
    for cmd in commands_in_category:
        print(f"  • {cmd}")
    print()
    
    success_count = 0
    for cmd_name in commands_in_category:
        print(f"Enabling {cmd_name}...")
        # Use silent update to avoid repeated messages
        if _silent_update_command(cmd_name, True):
            success_count += 1
    
    print()
    print_success(f"Enabled {success_count}/{len(commands_in_category)} commands in '{category}' category!")
    print_info("Use 'scionpathml show-cmds' to verify the changes")
    return True

def disable_commands_by_category(category: str) -> bool:
    """
    Disable all commands in a specific category
    
    Args:
        category (str): Category name
        
    Returns:
        bool: True if successful, False otherwise
    """
    print_header(f"DISABLING ALL {category.upper()} COMMANDS")
    
    config = load_command_config()
    if not config or not hasattr(config, 'PIPELINE_COMMANDS'):
        return False
    
    # Find commands in category
    commands_in_category = [
        cmd_name for cmd_name, cmd_config in config.PIPELINE_COMMANDS.items()
        if cmd_config.get('category', 'other') == category
    ]
    
    if not commands_in_category:
        print_error(f"No commands found in category '{category}'")
        return False
    
    print_warning(f"This will disable {len(commands_in_category)} commands:")
    for cmd in commands_in_category:
        print(f"  • {cmd}")
    print()
    
    success_count = 0
    for cmd_name in commands_in_category:
        print(f"Disabling {cmd_name}...")
        if _silent_update_command(cmd_name, False):
            success_count += 1
    
    print()
    print_success(f"Disabled {success_count}/{len(commands_in_category)} commands in '{category}' category!")
    return True

def enable_all_commands() -> bool:
    """Enable all pipeline commands"""
    print_header("ENABLING ALL PIPELINE COMMANDS")
    
    config = load_command_config()
    if not config or not hasattr(config, 'PIPELINE_COMMANDS'):
        return False
    
    success_count = 0
    total_count = len(config.PIPELINE_COMMANDS)
    
    print_info(f"Enabling {total_count} commands...")
    print()
    
    for cmd_name in config.PIPELINE_COMMANDS.keys():
        print(f"[ENABLE] {cmd_name}")
        if _silent_update_command(cmd_name, True):
            success_count += 1
    
    print()
    print_success(f"Enabled {success_count}/{total_count} pipeline commands!")
    print_info("Full pipeline will execute all measurement types")
    
    return True

def disable_all_commands() -> bool:
    """Disable all pipeline commands"""
    print_header("DISABLING ALL PIPELINE COMMANDS")
    
    config = load_command_config()
    if not config or not hasattr(config, 'PIPELINE_COMMANDS'):
        return False
    
    print_warning("IMPORTANT: This will disable ALL pipeline commands!")
    print("The pipeline will not execute any measurements until you re-enable commands.")
    print()
    print("Commands that will be disabled:")
    for cmd_name in config.PIPELINE_COMMANDS.keys():
        print(f"  • {cmd_name}")
    print()
    print("Are you sure you want to continue? (y/N): ", end="")
    
    try:
        response = input().strip().lower()
        if response != 'y':
            print_info("Operation cancelled - no changes made")
            return True
    except KeyboardInterrupt:
        print("\nOperation cancelled - no changes made")
        return True
    
    success_count = 0
    total_count = len(config.PIPELINE_COMMANDS)
    
    print()
    print_info("Disabling all commands...")
    
    for cmd_name in config.PIPELINE_COMMANDS.keys():
        print(f"[DISABLE] {cmd_name}")
        if _silent_update_command(cmd_name, False):
            success_count += 1
    
    print()
    print_success(f"Disabled {success_count}/{total_count} pipeline commands!")
    print_warning("Pipeline is now inactive - remember to enable needed commands")
    print()
    print_info("Quick recovery options:")
    print_example("scionpathml enable-all-cmds", "Re-enable all commands")
    print_example("scionpathml enable-cmd -m traceroute", "Enable only traceroute")
    print_example("scionpathml enable-category -c bandwidth", "Enable only bandwidth commands")
    
    return True

def _silent_update_command(cmd_name: str, enabled: bool) -> bool:
    """
    Silently update command without printing success/warning messages
    Used for batch operations
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return False
    
    # Update the specific command
    pattern = rf'("{cmd_name}": \{{[^}}]*"enabled": )(True|False)'
    replacement = rf'\g<1>{str(enabled)}'
    new_content = re.sub(pattern, replacement, content)
    
    if content == new_content:
        return True  # Already in desired state
    
    # Write back to file
    with open(CONFIG_FILE, "w") as f:
        f.write(new_content)
    
    return True

def show_command_help():
    """Show comprehensive help for command management"""
    print_header("PIPELINE COMMAND MANAGEMENT - COMPREHENSIVE GUIDE")
    
    print_section("WHAT IS COMMAND MANAGEMENT?")
    print("Command management lets you choose which parts of the SCION measurement")
    print("pipeline should run. Instead of always running all 7 commands, you can:")
    print("  • Enable only the commands you need (e.g., just traceroute)")
    print("  • Disable bandwidth-heavy commands to save resources")
    print("  • Create custom measurement workflows")
    print("  • Speed up pipeline execution by skipping unnecessary steps")
    
    print_section("AVAILABLE COMMANDS")
    
    default_commands = get_default_pipeline_commands()
    categories = {}
    for cmd_name, cmd_config in default_commands.items():
        category = cmd_config.get('category', 'other')
        if category not in categories:
            categories[category] = []
        categories[category].append((cmd_name, cmd_config))
    
    for category, commands in categories.items():
        print(f"\n{Colors.BOLD}{category.upper()} COMMANDS:{Colors.END}")
        
        for cmd_name, cmd_config in commands:
            print(f"  {Colors.CYAN}{cmd_name}{Colors.END}")
            print(f"    • Script: {cmd_config['script']}")
            print(f"    • Purpose: {cmd_config['description']}")
            print(f"    • Execution order: #{cmd_config['execution_order']}")
    
    print_section("QUICK START EXAMPLES")
    
    print(f"{Colors.BOLD}Scenario 1: Only want traceroute data{Colors.END}")
    print_example("scionpathml disable-all-cmds", "Disable everything first")
    print_example("scionpathml enable-cmd -m traceroute", "Enable only traceroute")
    print_example("scionpathml show-cmds", "Verify your setup")
    
    print(f"\n{Colors.BOLD}Scenario 2: Skip bandwidth tests (faster execution){Colors.END}")
    print_example("scionpathml disable-category -c bandwidth", "Disable all bandwidth commands")
    print_example("scionpathml show-cmds", "Check what's still enabled")
    
    print(f"\n{Colors.BOLD}Scenario 3: Only path discovery and analysis{Colors.END}")
    print_example("scionpathml disable-all-cmds", "Start fresh")
    print_example("scionpathml enable-cmd -m pathdiscovery", "Enable path discovery")
    print_example("scionpathml enable-cmd -m comparer", "Enable path comparison")
    
    print_section("ALL COMMAND MANAGEMENT OPTIONS")
    
    print(f"{Colors.BOLD}View Current Configuration:{Colors.END}")
    print_example("scionpathml show-cmds", "Display all commands and their status")
    
    print(f"\n{Colors.BOLD}Individual Command Control:{Colors.END}")
    print_example("scionpathml enable-cmd -m <command>", "Enable specific command")
    print_example("scionpathml disable-cmd -m <command>", "Disable specific command")
    
    print(f"\n{Colors.BOLD}Category-Based Control:{Colors.END}")
    print_example("scionpathml enable-category -c <category>", "Enable all commands in category")
    print_example("scionpathml disable-category -c <category>", "Disable all commands in category")
    
    print(f"\n{Colors.BOLD}Bulk Operations:{Colors.END}")
    print_example("scionpathml enable-all-cmds", "Enable all commands")
    print_example("scionpathml disable-all-cmds", "Disable all commands (with confirmation)")
    
    print_section("PARAMETER REFERENCE")
    
    print(f"{Colors.BOLD}Command Names (-m):{Colors.END}")
    cmd_names = list(default_commands.keys())
    for i in range(0, len(cmd_names), 2):
        line_cmds = cmd_names[i:i+2]
        print(f"  • {' • '.join(line_cmds)}")
    
    print(f"\n{Colors.BOLD}Category Names (-c):{Colors.END}")
    categories = list(set(cmd['category'] for cmd in default_commands.values()))
    for i in range(0, len(categories), 3):
        line_cats = categories[i:i+3]
        print(f"  • {' • '.join(line_cats)}")
    
    print_section("INTEGRATION WITH SCHEDULING")
    
    print("Command management works seamlessly with your existing scheduling:")
    print_example("scionpathml -f 30", "Set 30-minute frequency (respects enabled commands)")
    print_example("scionpathml show", "View both scheduling and command status")
    
    print()
    print_info("Use 'scionpathml show-cmds' anytime to see current configuration")

# Export all functions for CLI integration
__all__ = [
    'show_pipeline_commands',
    'update_pipeline_command', 
    'enable_commands_by_category',
    'disable_commands_by_category',
    'enable_all_commands',
    'disable_all_commands',
    'get_available_command_names',
    'get_available_categories',
    'validate_command_name',
    'show_command_help'
]