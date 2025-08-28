#Handles adding, updating, removing AS and servers
from .cli_utils import *
import datetime
from scionpathml.cli_tools.path_utils import collector_config

class ConfigManager:
    def __init__(self, config_file=None):
        if config_file is None:
            self.config_file = str(collector_config())
        else:
            self.config_file = config_file

    def show_config(self, cron_manager):
        """Display current configuration in a user-friendly format"""
        print_header("SCIONPATHML CONFIGURATION")
        
        config = load_config(self.config_file)
        if not config:
            return
        
        # Show AS Configuration
        print_section("AUTONOMOUS SYSTEMS (AS)")
        if hasattr(config, 'AS_TARGETS') and config.AS_TARGETS:
            for as_id, (ip, name) in config.AS_TARGETS.items():
                print(f"  {Colors.BOLD}{as_id}{Colors.END}")
                print(f"    • IP Address: {Colors.CYAN}{ip}{Colors.END}")
                print(f"    • AS Name: {Colors.CYAN}{name}{Colors.END}")
                print()
        else:
            print("  No AS configured yet")
            print()
            print_example("scionpathml add-as -a 19-ffaa:1:11de -i 192.168.1.100 -n MyAS", 
                         "Add your first AS")
            print()
        
        # Show Server Configuration  
        print_section("  BANDWIDTH TEST SERVERS")
        if hasattr(config, 'BWTEST_SERVERS') and config.BWTEST_SERVERS:
            for server_id, (ip, name) in config.BWTEST_SERVERS.items():
                print(f"  {Colors.BOLD}{server_id}{Colors.END}")
                print(f"    • IP Address: {Colors.CYAN}{ip}{Colors.END}")
                print(f"    • Server Name: {Colors.CYAN}{name}{Colors.END}")
                print()
        else:
            print("  No servers configured yet")
            print()
            print_example("scionpathml add-server -a 19-ffaa:1:22ef -i 10.0.0.50 -n TestServer", 
                         "Add your first server")
            print()
        
        # Show Pipeline Commands Status
        print_section(" PIPELINE COMMANDS")
        if hasattr(config, 'PIPELINE_COMMANDS') and config.PIPELINE_COMMANDS:
            # Count enabled/disabled commands
            enabled_cmds = [name for name, cfg in config.PIPELINE_COMMANDS.items() if cfg.get('enabled', True)]
            disabled_cmds = [name for name, cfg in config.PIPELINE_COMMANDS.items() if not cfg.get('enabled', True)]
            total_cmds = len(config.PIPELINE_COMMANDS)
            
            print(f"  Status Overview:")
            print(f"    • {Colors.GREEN}✓ Enabled: {len(enabled_cmds)}{Colors.END}")
            print(f"    • {Colors.RED}✗ Disabled: {len(disabled_cmds)}{Colors.END}")
            print(f"    • Total: {Colors.BOLD}{total_cmds}{Colors.END}")
            print()
            
            if enabled_cmds:
                print(f"  {Colors.GREEN}Active Commands:{Colors.END}")
                # Sort by execution order
                enabled_with_order = [(name, config.PIPELINE_COMMANDS[name].get('execution_order', 999)) for name in enabled_cmds]
                enabled_with_order.sort(key=lambda x: x[1])
                
                for i, (cmd_name, _) in enumerate(enabled_with_order, 1):
                    category = config.PIPELINE_COMMANDS[cmd_name].get('category', 'other')
                    print(f"    {i}. {Colors.BOLD}{cmd_name}{Colors.END} ({category})")
            
            if disabled_cmds:
                print()
                print(f"  {Colors.RED}Disabled Commands:{Colors.END}")
                for cmd_name in disabled_cmds:
                    category = config.PIPELINE_COMMANDS[cmd_name].get('category', 'other')
                    print(f"    • {Colors.RED}{cmd_name}{Colors.END} ({category})")
            
            print()
            print_info("Command Management:")
            print_example("scionpathml show-cmds", "View detailed command configuration")
            print_example("scionpathml cmd-help", "Learn about command management")
            
        else:
            print(f"  {Colors.YELLOW}⚠ Command configuration not found{Colors.END}")
            print("  All commands will run by default (backward compatibility)")
            print()
            print_info("Enable advanced command management:")
            print_example("scionpathml show-cmds", "Auto-create command configuration")
            print_example("scionpathml cmd-help", "Learn about selective execution")
            print()
        
        # Show Cron Status
        print_section("SCHEDULING STATUS")
        freq = cron_manager.get_current_cron_frequency()
        if freq is not None:
            print(f"  {Colors.GREEN}✓ Active{Colors.END} - Running every {Colors.BOLD}{freq} minutes{Colors.END}")
            
            # Calculate next execution time
            now = datetime.datetime.now()
            minutes_until_next = freq - (now.minute % freq)
            next_run = now + datetime.timedelta(minutes=minutes_until_next)
            print(f"  Next execution: ~{Colors.CYAN}{next_run.strftime('%H:%M')}{Colors.END}")
            
            # Show what will actually run
            if hasattr(config, 'PIPELINE_COMMANDS'):
                enabled_count = sum(1 for cfg in config.PIPELINE_COMMANDS.values() if cfg.get('enabled', True))
                print(f"Will execute: {Colors.BOLD}{enabled_count} commands{Colors.END}")
            
            # Show recommendation
            unique_ases = set(config.AS_FOLDER_MAP.keys()) | set(config.AS_TARGETS.keys())
            recommended = len(unique_ases) * 10
            if freq == recommended:
                print(f"  {Colors.GREEN}Optimal frequency{Colors.END}")
            elif freq < recommended:
                print(f"  {Colors.YELLOW}⚠ Consider {recommended} minutes for {len(unique_ases)} AS(es){Colors.END}")
            else:
                print(f"  {Colors.CYAN}Conservative setting (recommended: {recommended} min){Colors.END}")
        else:
            print(f"  {Colors.RED}✗ Not scheduled{Colors.END}")
            unique_ases = set(config.AS_FOLDER_MAP.keys()) | set(config.AS_TARGETS.keys())
            if unique_ases:
                recommended = len(unique_ases) * 10
                print()
                print_example(f"scionpathml -f {recommended}", 
                             f"Start scheduling for {len(unique_ases)} AS(es)")
        
        # Show summary statistics
        print_section("SUMMARY")
        as_count = len(set(config.AS_FOLDER_MAP.keys()) | set(config.AS_TARGETS.keys()))
        server_count = len(getattr(config, 'BWTEST_SERVERS', {}))
        print(f"  • Total AS: {Colors.BOLD}{as_count}{Colors.END}")
        print(f"  • Total Servers: {Colors.BOLD}{server_count}{Colors.END}")
        if hasattr(config, 'PIPELINE_COMMANDS'):
            enabled_cmd_count = sum(1 for cfg in config.PIPELINE_COMMANDS.values() if cfg.get('enabled', True))
            print(f"  • Active Commands: {Colors.BOLD}{enabled_cmd_count}{Colors.END}")
        if as_count > 0:
            recommended_freq = as_count * 10
            print(f"  • Recommended frequency: {Colors.BOLD}{recommended_freq} minutes{Colors.END}")
        
        print()
        print_info("Quick Actions:")
        print_example("scionpathml stop", "Stop automatic execution")
        print_example("scionpathml show-cmds", "Manage pipeline commands")

    def add_as(self, as_id, ip, name):
        """Add new Autonomous System"""
        print_header("ADDING NEW AUTONOMOUS SYSTEM")
        
        # Validate inputs
        errors = validate_inputs(as_id=as_id, ip=ip, name=name)
        if errors:
            print_error("Validation errors found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        config = load_config(self.config_file)
        if not config:
            return False
        
        # Check for duplicates
        if as_id in config.AS_FOLDER_MAP or as_id in config.AS_TARGETS:
            print_error(f"AS ID '{as_id}' already exists")
            print_info("Use 'up-as' to update existing AS or choose different ID")
            return False
            
        if name in config.AS_FOLDER_MAP.values():
            print_error(f"AS name '{name}' already exists")
            print_info("Choose a different name or update existing AS")
            return False
        
        # Update configuration
        success1 = update_config_section(self.config_file, "AS_FOLDER_MAP", as_id, f'"{name}"', silent=True)
        success2 = update_config_section(self.config_file, "AS_TARGETS", as_id, f'(\"{ip}\", \"{name}\")', silent=True)
        
        if success1 and success2:
            print_success(f"AS '{as_id}' added successfully!")
            print(f"  • AS ID: {as_id}")
            print(f"  • IP Address: {ip}")
            print(f"  • AS Name: {name}")
            return True
        return False

    def add_server(self, as_id, ip, name):
        """Add new bandwidth test server"""
        print_header("ADDING NEW BANDWIDTH TEST SERVER")
        
        # Validate inputs
        errors = validate_inputs(as_id=as_id, ip=ip, name=name)
        if errors:
            print_error("Validation errors found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        config = load_config(self.config_file)
        if not config:
            return False
        
        # Check for duplicates
        if as_id in config.BWTEST_SERVERS:
            print_error(f"Server ID '{as_id}' already exists")
            print_info("Use 'up-server' to update existing server or choose different ID")
            return False
            
        if name in [s[1] for s in config.BWTEST_SERVERS.values()]:
            print_error(f"Server name '{name}' already exists")
            print_info("Choose a different name or update existing server")
            return False
        
        # Update configuration
        success = update_config_section(self.config_file, "BWTEST_SERVERS", as_id, f'(\"{ip}\", \"{name}\")', silent=True)
        
        if success:
            print_success(f"Server '{as_id}' added successfully!")
            print(f"  • Server ID: {as_id}")
            print(f"  • IP Address: {ip}")
            print(f"  • Server Name: {name}")
            return True
        return False

    def remove_as(self, as_id):
        """Remove Autonomous System"""
        print_header("REMOVING AUTONOMOUS SYSTEM")
        
        # Validate AS ID format
        errors = validate_inputs(as_id=as_id)
        if errors:
            print_error("Validation errors found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        config = load_config(self.config_file)
        if not config:
            return False
        
        # Check if AS exists
        if as_id not in config.AS_FOLDER_MAP and as_id not in config.AS_TARGETS:
            print_error(f"AS ID '{as_id}' not found")
            print_info("Use 'scionpathml show' to see existing AS")
            return False
        
        # Remove from configuration
        success1 = update_config_section(self.config_file, "AS_FOLDER_MAP", as_id, None, remove=True, silent=True)
        success2 = update_config_section(self.config_file, "AS_TARGETS", as_id, None, remove=True, silent=True)
        
        if success1 or success2:
            print_success(f"AS '{as_id}' removed successfully!")
            return True
        return False

    def remove_server(self, as_id):
        """Remove bandwidth test server"""
        print_header("REMOVING BANDWIDTH TEST SERVER")
        
        # Validate AS ID format
        errors = validate_inputs(as_id=as_id)
        if errors:
            print_error("Validation errors found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        config = load_config(self.config_file)
        if not config:
            return False
        
        # Check if server exists
        if as_id not in config.BWTEST_SERVERS:
            print_error(f"Server ID '{as_id}' not found")
            print_info("Use 'scionpathml show' to see existing servers")
            return False
        
        # Remove from configuration
        success = update_config_section(self.config_file, "BWTEST_SERVERS", as_id, None, remove=True, silent=True)
        
        if success:
            print_success(f"Server '{as_id}' removed successfully!")
            return True
        return False

    def update_as(self, as_id, ip, name):
        """Update existing Autonomous System"""
        print_header("UPDATING AUTONOMOUS SYSTEM")
        
        # Validate inputs
        errors = validate_inputs(as_id=as_id, ip=ip, name=name)
        if errors:
            print_error("Validation errors found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        config = load_config(self.config_file)
        if not config:
            return False
        
        # Check if AS exists
        if as_id not in config.AS_FOLDER_MAP and as_id not in config.AS_TARGETS:
            print_error(f"AS ID '{as_id}' does not exist")
            print_info("Use 'add-as' to create new AS or check existing AS with 'show'")
            return False
            
        # Check if new name conflicts with other AS
        for existing_as_id, as_name in config.AS_FOLDER_MAP.items():
            if as_name == name and existing_as_id != as_id:
                print_error(f"AS name '{name}' already used by AS '{existing_as_id}'")
                print_info("Choose a different name")
                return False
        
        # Update configuration
        success1 = update_config_section(self.config_file, "AS_FOLDER_MAP", as_id, f'"{name}"', silent=True)
        success2 = update_config_section(self.config_file, "AS_TARGETS", as_id, f'(\"{ip}\", \"{name}\")', silent=True)
        
        if success1 and success2:
            print_success(f"AS '{as_id}' updated successfully!")
            print(f"  • AS ID: {as_id}")
            print(f"  • New IP Address: {ip}")
            print(f"  • New AS Name: {name}")
            return True
        return False

    def update_server(self, as_id, ip, name):
        """Update existing bandwidth test server"""
        print_header("UPDATING BANDWIDTH TEST SERVER")
        
        # Validate inputs
        errors = validate_inputs(as_id=as_id, ip=ip, name=name)
        if errors:
            print_error("Validation errors found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        config = load_config(self.config_file)
        if not config:
            return False
        
        # Check if server exists
        if as_id not in config.BWTEST_SERVERS:
            print_error(f"Server ID '{as_id}' does not exist")
            print_info("Use 'add-server' to create new server or check existing servers with 'show'")
            return False
            
        # Check if new name conflicts with other servers
        for server_id, (server_ip, server_name) in config.BWTEST_SERVERS.items():
            if server_name == name and server_id != as_id:
                print_error(f"Server name '{name}' already used by server '{server_id}'")
                print_info("Choose a different name")
                return False
        
        # Update configuration
        success = update_config_section(self.config_file, "BWTEST_SERVERS", as_id, f'(\"{ip}\", \"{name}\")', silent=True)
        
        if success:
            print_success(f"Server '{as_id}' updated successfully!")
            print(f"  • Server ID: {as_id}")
            print(f"  • New IP Address: {ip}")
            print(f"  • New Server Name: {name}")
            return True
        return False