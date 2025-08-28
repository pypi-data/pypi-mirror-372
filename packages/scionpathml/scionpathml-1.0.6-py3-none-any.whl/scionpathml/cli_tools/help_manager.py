#Main help system with guides 
from .cli_utils import *

class HelpManager:
    @staticmethod
    def show_help():
        """Show quick start guide only"""
        print_header("SCIONPATHML CLI - QUICK START GUIDE")
        
        print_section("GETTING STARTED")
        print("Set up for SCIONPATHML:")
        print()
        print("Step 1: Add your AS")
        print_example("scionpathml add-as -a 19-ffaa:1:11de -i 192.168.1.100 -n MyAS", 
                     "Replace with your actual AS details")
        
        print("\nStep 2: Add a server for bandwidth tests")
        print_example("scionpathml add-server -a 19-ffaa:1:22ef -i 10.0.0.50 -n TestServer", 
                     "This is necessary for bandwidth command")
        
        print("\nStep 3: Test everything works")
        print_example("scionpathml run", "Run the pipeline once to make sure it works")
        
        print("\nStep 4: Set it to run automatically")
        print_example("scionpathml -f 40", "Every 40 minutes works well for most setups")
        
        print("\nStep 5: Check your results")
        print_example("scionpathml data-browse", "Browse through your measurement data")
        
        print_section("MORE HELP AVAILABLE")
        print_example("scionpathml help-config", "AS and server management")
        print_example("scionpathml help-examples", "Examples and best practices")
        print_example("scionpathml help-troubleshooting", "When things go wrong")
        print_example("scionpathml cmd-help", "Command management guide")
        print_example("scionpathml data-help", "Data management guide")
        print_example("scionpathml log-help", "Log viewing guide")
        print_example("scionpathml transform-help", "Data transformation guide")
        print_example("scionpathml show", "Check current status")
        
        print_section("COMMON FIRST STEPS")
        print_example("scionpathml show-cmds", "See what measurements are enabled")
        print_example("scionpathml disable-cmd -m bandwidth", "Turn off heavy bandwidth tests")
        print_example("scionpathml data-overview", "See what data you already have")
        

    @staticmethod
    def show_examples_help():
        """Show examples and best practices"""
        print_header("SCIONPATHML CLI - EXAMPLES & BEST PRACTICES")
        
        print_section("COMMON WORKFLOWS")
        
        print(f"{Colors.BOLD}Initial Setup:{Colors.END}")
        print_example("scionpathml add-as -a 19-ffaa:1:11de -i 10.0.0.1 -n MyAS", "Add your AS")
        print_example("scionpathml add-server -a 19-ffaa:1:22ef -i 10.0.0.50 -n MyServer", "Add your server")
        print_example("scionpathml show-cmds", "Check what will run")
        print_example("scionpathml run", "Test everything works")
        print_example("scionpathml -f 40", "Schedule regular runs")
        
        print(f"\n{Colors.BOLD}Data Management:{Colors.END}")
        print_example("scionpathml data-overview", "Check what you have")
        print_example("scionpathml data-browse", "Browse files interactively")
        print_example("scionpathml data-move Archive History", "Archive old data")
        print_example("scionpathml transform", "Convert to CSV for analysis")
        
        print(f"\n{Colors.BOLD}Performance Tuning:{Colors.END}")
        print_example("scionpathml disable-category -c bandwidth", "Skip heavy bandwidth tests")
        print_example("scionpathml disable-cmd -m mp-bandwidth", "Disable multipath bandwidth")
        print_example("scionpathml enable-cmd -m traceroute", "Enable lightweight traceroute")
        print_example("scionpathml -f 60", "Use longer intervals for many AS")
        
        print(f"\n{Colors.BOLD}Debugging Issues:{Colors.END}")
        print_example("scionpathml logs pipeline --all", "Check what went wrong")
        print_example("scionpathml run", "Test run manually")
        print_example("python3 collector/pathdiscovery.py", "Test individual script")
        print_example("scionpathml show", "Verify configuration")
        
        print_section("FREQUENCY GUIDELINES")
        print()
        print("10 minutes per AS")
        print("• 2 AS => Every 20 minutes")
        print("• 4 AS => Every 40 minutes")  
        print()
        print_example("scionpathml run", "Always test timing manually first")
        
        print_section("DATA ORGANIZATION")
        print()
        print_example("scionpathml data-move History Archive", "Archive old measurements")
        print_example("scionpathml data-delete History --category Comparer", "Clean up old comparisons")
        print_example("scionpathml data-move Archive /backup/$(date +%Y-%m)", "Monthly backup")
        print_example("scionpathml transform", "Convert before archiving")

    @staticmethod
    def show_troubleshooting_help():
        """Show troubleshooting guide"""
        print_header("SCIONPATHML CLI - TROUBLESHOOTING")
        
        print_section("SCRIPT PATH ISSUES")
        print("If you get 'script not found' errors:")
        print_example("export SCRIPT_PATH=/path/to/runner", "Set environment variable")
        print("Or check that you're running from the right directory")
        
        
        print_section("NO DATA BEING GENERATED")
        print("If measurements run but create no files:")
        print()
        print("1. Check enabled commands:")
        print_example("scionpathml show-cmds", "See what's actually enabled")
        
        print("\n2. Check if individual scripts work:")
        print_example("python3 collector/pathdiscovery.py", "Test individual script")
        
        print("\n3. Check network connectivity:")
        print("• Make sure your AS is reachable")
        print("• Verify SCION infrastructure is running")
        print("• Check firewall settings")
        
        print_section("DATA MANAGEMENT ISSUES")
        print(f"{Colors.BOLD}'No JSON files found':{Colors.END}")
        print("• Check the data path contains .json files")
        print_example("ls -la Data/Archive/", "See what's actually there")
        
        print(f"\n{Colors.BOLD}Move/delete fails:{Colors.END}")
        print("• Ensure destination path is accessible")
        
        print_section("LOG ISSUES")
        print("If no log files appear:")
        print("• Check if measurements are actually running")
        print("• Ensure pipeline has executed at least once")
        print_example("ls -la Data/Logs/", "Check log directory")
        
        print_section("CRON/SCHEDULING ISSUES")
        print("If scheduled runs don't work:")
        print_example("systemctl status cron", "Check if cron service is running")
        print_example("crontab -l", "See your current cron jobs")
        print_example("tail -f /var/log/cron", "Watch cron logs")
        print("Always test manually with 'scionpathml run' before scheduling!")
        
        print_section(" GETTING MORE HELP")
        print_example("scionpathml logs pipeline --all", "Full pipeline log")
        print_example("scionpathml show", "Current configuration")
        print_example("scionpathml data-overview", "What data exists")

    @staticmethod
    def show_welcome():
        """Show welcome message when no arguments provided"""
        print_header("WELCOME TO SCIONPATHML")
        print()
        
        print_section("QUICK START")
        print_example("scionpathml run", "Test run the pipeline right now")
        print_example("scionpathml show", "See your current configuration")
        print_example("scionpathml help", "Quick start guide")
        print()
        
        print_section("CHECK YOUR DATA")
        print_example("scionpathml data-overview", "Quick overview of your measurement files")
        print_example("scionpathml data-browse", "Browse files interactively (recommended)")
        print_example("scionpathml logs pipeline", "Check if measurements are running")
        print()
        
        print_section("CONFIGURATION")
        print_example("scionpathml show-cmds", "See what measurements are enabled")
        print_example("scionpathml -f 30", "Schedule to run every 30 minutes")
        print_example("scionpathml add-as -a YOUR_AS -i YOUR_IP -n NAME", "Add an AS to monitor")
        print()
        
        print_section("DATA MANAGEMENT")
        print_example("scionpathml transform", "Convert JSON files to CSV")
        print_example("scionpathml data-search BW_2025", "Search for specific files")
        print_example("scionpathml data-move Archive /backup", "Backup your data")
        print()
        
        print_section("HELP & DOCS")
        print_example("scionpathml help", "Quick start guide")
        print_example("scionpathml help-config", "AS and server management")
        print_example("scionpathml help-examples", "Examples and workflows")
        print_example("scionpathml help-troubleshooting", "When things break")
        print_example("scionpathml cmd-help", "Command management details")
        print_example("scionpathml data-help", "Data management options")
        print_example("scionpathml log-help", "Log viewing guide")
        print_example("scionpathml transform-help", "Data transformation guide")