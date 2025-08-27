#Main CLI entry point and argument parsing
import argparse
import sys
from command_manager import (
    show_pipeline_commands,
    update_pipeline_command, 
    enable_commands_by_category,
    disable_commands_by_category,
    enable_all_commands,
    disable_all_commands,
    get_available_command_names,
    get_available_categories,
    show_command_help
)
from log_commands import LogCommands, LogHelpDisplay
from cli_utils import *
from cron_manager import CronManager
from config_manager import ConfigManager
from help_manager import HelpManager
from transform_commands import TransformCommands
from data_commands import DataCommands
from config_help import ConfigHelpManager

def main():
    # MINIMAL FIX: Handle transform-data with path before argparse
    if len(sys.argv) > 1 and sys.argv[1] == 'transform-data':
        if len(sys.argv) < 3:
            print_error("Missing data path for transform-data command")
            print_example("scionpathml transform-data /path/to/json", "Correct usage")
            sys.exit(1)
        
        data_path = sys.argv[2]
        transform_type = 'all'  # default
        output_dir = None
        
        # Parse optional arguments
        for i in range(3, len(sys.argv)):
            if sys.argv[i] == '--output-dir' and i + 1 < len(sys.argv):
                output_dir = sys.argv[i + 1]
            elif sys.argv[i] in ['standard', 'multipath', 'all'] and not sys.argv[i].startswith('--'):
                transform_type = sys.argv[i]
        
        # Initialize and run transform
        transform_commands = TransformCommands()
        transform_commands.handle_transform_data_command(data_path, transform_type, output_dir)
        sys.exit(0)

    # Initialize managers
    cron_manager = CronManager()
    config_manager = ConfigManager()
    help_manager = HelpManager()
    transform_commands = TransformCommands()
    data_commands = DataCommands()
    
    parser = argparse.ArgumentParser(
        prog="scionpathml",
        description=f"""
{Colors.BOLD}{Colors.BLUE} ScionPahML CLI{Colors.END}
{Colors.CYAN}Manage AS & Server Configuration + Pipeline Commands + Scheduling + Log Viewing{Colors.END}

{Colors.BOLD}Quick Examples:{Colors.END}
  {Colors.GREEN}scionpathml run{Colors.END}                 (test pipeline once)
  {Colors.GREEN}scionpathml add-as -a 19-ffaa:1:11de -i 10.0.0.1 -n AS-1{Colors.END}
  {Colors.GREEN}scionpathml show-cmds{Colors.END}           (view/manage pipeline commands)
  {Colors.GREEN}scionpathml data-browse{Colors.END}         (interactive data browser)
  {Colors.GREEN}scionpathml -f 40{Colors.END}               (set 40-minute frequency)

{Colors.BOLD}Help Commands:{Colors.END}
  {Colors.GREEN}scionpathml help{Colors.END}                (quick start guide)
  {Colors.GREEN}scionpathml help-examples{Colors.END}       (examples & workflows)  
  {Colors.GREEN}scionpathml help-troubleshooting{Colors.END} (when things break)
            """,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
        epilog=f"""
{Colors.BOLD}DETAILED EXAMPLES:{Colors.END}

{Colors.CYAN}Pipeline Execution:{Colors.END}
  scionpathml run                      # Execute pipeline once
  scionpathml -f 30                    # Schedule to run every 30 minutes
  scionpathml stop                     # Stop scheduled execution

{Colors.CYAN}Data Management:{Colors.END}
  scionpathml data-overview            # Show overview of all data directories
  scionpathml data-browse              # Interactive data browser (recommended!)
  scionpathml data-move Archive History # Move Archive files to History
  scionpathml data-help               # Complete data management guide

{Colors.CYAN}Getting Help:{Colors.END}
  scionpathml help                    # Quick start guide
  scionpathml help-config             # AS and server management
  scionpathml help-examples           # Examples and best practices  
  scionpathml help-troubleshooting    # When things go wrong
  scionpathml cmd-help                # Command management guide
  scionpathml log-help                # Log viewing guide
  scionpathml data-help               # Data management guide

{Colors.YELLOW} Start with 'scionpathml help' for the basics{Colors.END}
            """)

    parser.add_argument(
        'command',
        nargs='?',
        choices=[
            'stop', 'show', 'help', 'run',
            'help-examples', 'help-troubleshooting','help-config',
            'add-as', 'add-server',
            'rm-as', 'rm-server', 
            'up-as', 'up-server',
            'show-cmds', 'enable-cmd', 'disable-cmd',           
            'enable-category', 'disable-category',                
            'enable-all-cmds', 'disable-all-cmds',                     
            'cmd-help',   
            'logs',      
            'view-log',
            'log-help',
            'transform',      
            'transform-status',    
            'transform-help',
            'data-overview', 
            'data-show',
            'data-browse',    
            'data-move', 
            'data-delete', 
            'data-search', 
            'data-help'                                     
        ],
        help="""
Command to execute:
  show        - Display current configuration and status
  stop        - Stop automatic execution (remove cron job)
  run         - Execute pipeline once immediately
  help        - Quick start guide
  help-examples         - Examples and best practices
  help-troubleshooting  - Troubleshooting guide
  help-config          - AS and server management guide
  add-as      - Add new Autonomous System
  add-server  - Add new bandwidth test server  
  rm-as       - Remove Autonomous System
  rm-server   - Remove bandwidth test server
  up-as       - Update existing Autonomous System
  up-server   - Update existing bandwidth test server
  logs        - View logs (pipeline, bandwidth, traceroute, etc.)
  view-log    - View specific log file
  log-help    - Log viewing guide
  transform         - Transform data from Data/Archive (default)
  transform-status  - Show transformation status
  transform-help    - Transformation help guide
  data-overview     - Show overview of all data directories
  data-show         - Show detailed directory contents
  data-browse       - Interactive data browser
  data-move         - Move data between directories
  data-delete       - Delete data from directories
  data-search       - Search for files
  data-help         - Data management help
            """
    )
    
    # Arguments
    parser.add_argument("-m", type=str, help="Command module name (e.g., bandwidth, traceroute, prober)")
    parser.add_argument("-f", type=int, help="Set script frequency in minutes (e.g., 30 for every 30 minutes)")
    parser.add_argument("-p", type=str, help="Override path to runner directory containing pipeline.sh")
    parser.add_argument("-a", type=str, help="AS ID in format: number-ffaa:hex:hex (e.g., 19-ffaa:1:11de)")
    parser.add_argument("-i", type=str, help="IPv4 address (e.g., 192.168.1.100)")
    parser.add_argument("-n", type=str, help="Name for AS folder or server (alphanumeric + hyphens/underscores)")
    parser.add_argument("-c", type=str, help="Category name for commands (e.g., bandwidth, tracing)")
    parser.add_argument('log_category', nargs='?', help='Log category (pipeline, bandwidth, traceroute, etc.)')
    parser.add_argument('file_number', nargs='?', help='File number or "latest"')
    parser.add_argument('--log-dir', type=str, default="Data/Logs/", help='Log directory path')
    parser.add_argument('--all', action='store_true', help='Show entire log file instead of just last lines')
    parser.add_argument('--interactive', action='store_true', help='Enable interactive mode for data commands')
    parser.add_argument('--output-dir', type=str, help='Custom output directory for CSV files')
    parser.add_argument('--category', type=str, help='Category for data operations (Bandwidth, Traceroute, etc.)')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompts')

    # Handle no arguments
    if len(sys.argv) == 1:
        help_manager.show_welcome()
        sys.exit(0)

    # Parse arguments
    args = parser.parse_args()
    
    # Initialize log commands
    log_commands = LogCommands(args.log_dir)

    # Handle help commands
    if args.command == "help":
        help_manager.show_help()
        sys.exit(0)
    elif args.command == "help-examples":
        help_manager.show_examples_help()
        sys.exit(0)
    elif args.command == "help-troubleshooting":
        help_manager.show_troubleshooting_help()
        sys.exit(0)
    
    elif args.command == "help-config":
        ConfigHelpManager.show_config_help()
        sys.exit(0)

    # Load configuration for commands that need it
    config = None
    if args.command in ['show', 'add-as', 'add-server', 'rm-as', 'rm-server', 'up-as', 'up-server'] or args.f:
        config = load_config()
        if not config and args.command != 'show':
            sys.exit(1)
    

    # Command handlers
    if args.command == "stop":
        cron_manager.stop_cron()

    elif args.command == "run":
        cron_manager.run_once()
        
    elif args.command == "show":
        config_manager.show_config(cron_manager)
        
    elif args.command == "add-as":
        if not (args.a and args.i and args.n):
            print_error("Missing required parameters for add-as")
            print_info("Required: AS ID (-a), IP address (-i), and name (-n)")
            print_example("scionpathml add-as -a 19-ffaa:1:11de -i 192.168.1.100 -n MyAS", "Complete example")
            sys.exit(1)
        
        if config_manager.add_as(args.a, args.i, args.n):
            cron_manager.check_frequency_warning(load_config())
        
    elif args.command == "add-server":
        if not (args.a and args.i and args.n):
            print_error("Missing required parameters for add-server")
            print_info("Required: AS ID (-a), IP address (-i), and name (-n)")
            print_example("scionpathml add-server -a 19-ffaa:1:22ef -i 10.0.0.50 -n TestServer", "Complete example")
            sys.exit(1)
        
        if config_manager.add_server(args.a, args.i, args.n):
            cron_manager.check_frequency_warning(load_config())
        
    elif args.command == "rm-as":
        if not args.a:
            print_error("Missing AS ID parameter")
            print_example("scionpathml rm-as -a 19-ffaa:1:11de", "Remove specific AS")
            sys.exit(1)
        
        if config_manager.remove_as(args.a):
            cron_manager.check_frequency_warning(load_config())
        
    elif args.command == "rm-server":
        if not args.a:
            print_error("Missing server ID parameter")
            print_example("scionpathml rm-server -a 19-ffaa:1:22ef", "Remove specific server")
            sys.exit(1)
        
        config_manager.remove_server(args.a)
        
    elif args.command == "up-as":
        if not (args.a and args.i and args.n):
            print_error("Missing required parameters for up-as")
            print_info("Required: AS ID (-a), IP address (-i), and name (-n)")
            print_example("scionpathml up-as -a 19-ffaa:1:11de -i 192.168.1.101 -n UpdatedAS", "Complete example")
            sys.exit(1)
        
        if config_manager.update_as(args.a, args.i, args.n):
            cron_manager.check_frequency_warning(load_config())
        
    elif args.command == "up-server":
        if not (args.a and args.i and args.n):
            print_error("Missing required parameters for up-server")
            print_info("Required: Server ID (-a), IP address (-i), and name (-n)")
            print_example("scionpathml up-server -a 19-ffaa:1:22ef -i 10.0.0.51 -n UpdatedServer", "Complete example")
            sys.exit(1)
        
        config_manager.update_server(args.a, args.i, args.n)

    # Pipeline command management
    elif args.command == "show-cmds":
        show_pipeline_commands()
        
    elif args.command == "enable-cmd":
        if not args.m:
            print_error("Missing command name (-m)")
            print_info("Available commands:")
            for cmd in get_available_command_names():
                print(f"  • {cmd}")
            print_example("scionpathml enable-cmd -m bandwidth", "Enable bandwidth command")
            sys.exit(1)
        update_pipeline_command(args.m, True)
        
    elif args.command == "disable-cmd":
        if not args.m:
            print_error("Missing command name (-m)")
            print_info("Available commands:")
            for cmd in get_available_command_names():
                print(f"  • {cmd}")
            print_example("scionpathml disable-cmd -m traceroute", "Disable traceroute command")
            sys.exit(1)
        update_pipeline_command(args.m, False)
        
    elif args.command == "enable-category":
        if not args.c:
            print_error("Missing category name (-c)")
            print_info("Available categories:")
            for cat in get_available_categories():
                print(f"  • {cat}")
            print_example("scionpathml enable-category -c bandwidth", "Enable all bandwidth commands")
            sys.exit(1)
        enable_commands_by_category(args.c)
        
    elif args.command == "disable-category":
        if not args.c:
            print_error("Missing category name (-c)")
            print_info("Available categories:")
            for cat in get_available_categories():
                print(f"  • {cat}")
            print_example("scionpathml disable-category -c probing", "Disable all probing commands")
            sys.exit(1)
        disable_commands_by_category(args.c)
        
    elif args.command == "enable-all-cmds":
        enable_all_commands()
        
    elif args.command == "disable-all-cmds":
        disable_all_commands()
        
    elif args.command == "cmd-help":
        show_command_help()   

    # Log management
    elif args.command == "logs":
        log_commands.handle_logs_command(args.log_category, show_all=args.all)
    
    elif args.command == "view-log":
        file_selector = args.file_number
        log_commands.handle_view_log_command(args.log_category, file_selector, args.all)   
        
    elif args.command == "log-help":
        LogHelpDisplay.show_log_quick_reference()
        
    # Transform management
    elif args.command == "transform":
        # Simple transform command using default Data/Archive path
        # Parse transform type from positional args if available
        transform_type = None
        if hasattr(args, 'log_category') and args.log_category in ['standard', 'multipath', 'all']:
            transform_type = args.log_category
        transform_commands.handle_transform_command(transform_type, args.output_dir)

    elif args.command == "transform-status":
        transform_commands.handle_transform_status_command(args.output_dir)
        
    elif args.command == "transform-help":
        transform_commands.handle_transform_help_command()
        
    # Data management commands
    elif args.command == "data-overview":
        data_commands.handle_data_overview_command()

    elif args.command == "data-show":
        # Handle --interactive flag for data-show
        data_commands.handle_data_show_command(args.log_category, interactive=args.interactive)

    elif args.command == "data-browse":
        # New interactive browse command
        data_commands.handle_data_browse_command(args.log_category)

    elif args.command == "data-move":
        source = args.log_category
        dest = args.file_number
        data_commands.handle_data_move_command(source, dest, args.category, args.no_confirm)

    elif args.command == "data-delete":
        data_commands.handle_data_delete_command(args.log_category, args.category, args.no_confirm)

    elif args.command == "data-search":
        pattern = args.log_category
        directory = args.file_number
        data_commands.handle_data_search_command(pattern, directory)

    elif args.command == "data-help":
        data_commands.handle_data_help_command()

    # Frequency management
    elif args.f:
        try:
            if cron_manager.update_cron(args.f, args.p, config):
                print()
                print_info("Next steps:")
                print_example("scionpathml show", "Check your configuration")
                print_example("crontab -l", "View all your cron jobs")
        except EnvironmentError as e:
            print_error(str(e))
            sys.exit(1)
            
    else:
        print_header("SCIONPATHML CLI")
        print_error("No valid command or option provided")
        print()
        print_info("Quick start options:")
        print_example("scionpathml show", "View current configuration")
        print_example("scionpathml help", "See quick start guide") 
        print_example("scionpathml help-examples", "See examples and workflows")
        print_example("scionpathml -h", "View quick command reference")
        print()
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
        