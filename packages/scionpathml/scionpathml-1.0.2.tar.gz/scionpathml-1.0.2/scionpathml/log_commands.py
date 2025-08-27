#Commands for viewing and managing log files
from log_manager import SimpleLogManager
from log_display import LogDisplay, print_error, print_example, print_header, print_section, print_info, Colors
import sys

class LogCommands:
    """Handle log-related CLI commands"""
    
    def __init__(self, log_dir="Data/Logs/"):
        self.log_manager = SimpleLogManager(log_dir)
        self.display = LogDisplay()
    
    def handle_logs_command(self, category=None, show_all=False):
        """Handle 'logs' command with optional --all flag"""
        if not category:
            self.display.show_logs_overview(self.log_manager)
            return
        
        if not self.log_manager.validate_category(category):
            print_error(f"Invalid category: {category}")
            print_error("Valid categories: pipeline, bandwidth, traceroute, prober, comparer, showpaths, mp-bandwidth, mp-prober")
            return
        
        if category.lower() == "pipeline":
            self.display.show_pipeline_log(self.log_manager, show_all=show_all)
        else:
            self.display.show_category_files(self.log_manager, category)
    
    def handle_view_log_command(self, category, file_selector=None, show_all=False):
        """Handle 'view-log' command - defaults to first file if no selector provided"""
        if not category:
            print_error("Missing log category")
            print()
            print_example("scionpathml view-log pipeline", "View pipeline.log")
            print_example("scionpathml view-log bandwidth", "View first bandwidth log (default)")
            print_example("scionpathml view-log bandwidth 1", "View bandwidth log #1")
            print_example("scionpathml view-log bandwidth latest", "View latest bandwidth log")
            print_example("scionpathml view-log traceroute latest --all", "View entire latest traceroute log")
            return
        
        if not self.log_manager.validate_category(category):
            print_error(f"Invalid category: {category}")
            print_error("Valid categories: pipeline, bandwidth, traceroute, prober, comparer, showpaths, mp-bandwidth, mp-prober")
            return
        
        # file_selector is None when no file is specified - this will default to first file
        self.display.show_specific_log(self.log_manager, category, file_selector, show_all)
    
    def show_log_help_section(self):
        """Return log help section for main CLI help"""
        return f"""
    print_section(" SIMPLE LOG VIEWING")
    
    print(f"{Colors.BOLD}Basic Log Commands:{Colors.END}")
    print_example("scionpathml logs", "Show all available logs")
    print_example("scionpathml logs pipeline", "View pipeline.log (last 30 lines)")
    print_example("scionpathml logs bandwidth", "List bandwidth log files") 
    print_example("scionpathml logs pipeline --all", "View entire pipeline.log")
    print_example("scionpathml logs traceroute", "List traceroute log files")
    
    print(f"\\n{Colors.BOLD}View Specific Files:{Colors.END}")
    print_example("scionpathml view-log pipeline", "View pipeline.log (last 50 lines)")
    print_example("scionpathml view-log bandwidth", "View first bandwidth file (DEFAULT)")
    print_example("scionpathml view-log bandwidth 1", "View bandwidth file #1 (last 50 lines)")
    print_example("scionpathml view-log bandwidth latest", "View latest bandwidth file")
    print_example("scionpathml view-log traceroute latest", "View latest traceroute (last 50 lines)")
    print_example("scionpathml view-log prober 3", "View prober file #3 (last 50 lines)")
    
    print(f"\\n{Colors.BOLD}View Complete Files:{Colors.END}")
    print_example("scionpathml view-log pipeline --all", "View entire pipeline.log")
    print_example("scionpathml view-log bandwidth --all", "View complete first bandwidth file")
    print_example("scionpathml view-log bandwidth latest --all", "View complete latest bandwidth file")
    print_example("scionpathml view-log bandwidth 1 --all", "View complete bandwidth file #1")
    print_example("scionpathml view-log traceroute latest --all", "View complete latest traceroute")
    
    print(f"\\n{Colors.BOLD}Log Navigation Tips:{Colors.END}")
    print("  • Default behavior shows first file in list")
    print("  • Use 'latest' to view highest numbered file")
    print("  • Default view shows last 30-50 lines (most recent activity)")
    print("  • Use --all flag to see complete file")
    print("  • Large files (100+ lines) show with pagination:")
    print("    - Press Enter: Next page")
    print("    - Type 'q': Quit viewing")
    print("    - Type page number: Jump to specific page")
    print("  • Log levels are status-coded:")
    print("    [ERROR] Errors/Failures  [WARNING] Warnings  [INFO] Info  [DEBUG] Debug")
        """
    
    def show_log_parameter_formats(self):
        """Return log parameter formats section"""
        return f"""
    print_section("LOG PARAMETER FORMATS")
    
    print(f"{Colors.BOLD}Log Categories:{Colors.END}")
    print("  • pipeline     - Main pipeline execution log (pipeline.log)")
    print("  • bandwidth    - Bandwidth measurement logs")  
    print("  • traceroute   - Network path tracing logs")
    print("  • prober       - Network probing logs")
    print("  • comparer     - Path comparison logs")
    print("  • showpaths    - Available paths logs")
    print("  • mp-bandwidth - Multi-path bandwidth logs")
    print("  • mp-prober    - Multi-path probing logs")
    
    print(f"\\n{Colors.BOLD}File Selection:{Colors.END}")
    print("  • No file specified - First file in list - DEFAULT")
    print("  • latest       - Highest numbered file")
    print("  • 1, 2, 3...   - File number from list")
    print("  • Example: 'scionpathml logs bandwidth' shows numbered list")
    
    print(f"\\n{Colors.BOLD}Log Display Options:{Colors.END}")
    print("  • Default      - Shows last 30-50 lines")
    print("  • --all        - Shows entire file with pagination")
    print("  • --log-dir    - Custom log directory path")
        """
    
    def show_log_troubleshooting(self):
        """Return log troubleshooting section"""
        return f"""
    print(f"\\n{Colors.BOLD}Log Viewing Issues:{Colors.END}")
    
    print("• If logs directory not found:")
    print_example("scionpathml logs --log-dir /path/to/logs", "Use custom log directory")
    
    print("\\n• If no log files in category:")
    print("  - Check if measurements are running:")
    print_example("scionpathml show", "Check pipeline status")
    print("  - Verify log directory permissions")
    print("  - Ensure pipeline has executed at least once")
    
    print("\\n• If pipeline.log is empty or missing:")
    print("  - Pipeline might not have run yet:")
    print_example("crontab -l", "Check if cron job is set")
    print_example("scionpathml -f 30", "Set up scheduling")
    print("  - Check script permissions and paths")
    
    print("\\n• For large log files:")
    print("  - Use default view first (last 30-50 lines)")
    print("  - Only use --all for detailed investigation")
    print("  - Use pagination controls: Enter (next), 'q' (quit), number (jump)")
    
    print("\\n• Understanding log status indicators:")
    print("  [ERROR] - Errors, failures, exceptions - need attention")
    print("  [WARNING] - Warnings - might need attention")  
    print("  [INFO] - Information messages - normal operation")
    print("  [DEBUG] - Debug messages - detailed activity")
    print("  (no prefix) - General messages - normal activity")
        """
    
    def show_log_epilog_examples(self):
        """Return log examples for CLI epilog"""
        return f"""
{Colors.CYAN}Log Management:{Colors.END}
  scionpathml logs                         # List all log categories
  scionpathml logs pipeline               # View pipeline.log (last 30 lines)
  scionpathml logs bandwidth              # List bandwidth log files
  scionpathml logs pipeline --all         # View entire pipeline.log
  scionpathml view-log pipeline           # View pipeline.log (last 50 lines)
  scionpathml view-log pipeline --all     # View entire pipeline.log
  scionpathml view-log bandwidth          # View first bandwidth file (DEFAULT)
  scionpathml view-log bandwidth latest   # View latest bandwidth file
  scionpathml view-log bandwidth 1        # View bandwidth file #1 (last 50 lines)
  scionpathml view-log bandwidth 1 --all  # View complete bandwidth file #1
  scionpathml view-log traceroute latest  # View latest traceroute (last 50 lines)
  scionpathml view-log traceroute latest --all  # View complete traceroute
        """
    
    def show_log_no_args_section(self):
        """Return log section for no-arguments display"""
        return f"""
    print_section("VIEW YOUR LOGS")
    print_example("scionpathml logs", "See available log categories")
    print_example("scionpathml logs pipeline", "Quick view of pipeline.log")
    print_example("scionpathml logs pipeline --all", "View complete pipeline.log")
    print_example("scionpathml view-log bandwidth", "View first bandwidth file")
    print_example("scionpathml view-log bandwidth latest", "View latest bandwidth file")
    print_example("scionpathml view-log pipeline --all", "View complete pipeline.log")
    print_example("scionpathml logs bandwidth", "Browse bandwidth logs")
        """

class LogHelpDisplay:
    """Dedicated class for log help and documentation"""
    
    @staticmethod
    def show_log_quick_reference():
        """Show quick log reference"""
        print_header("LOG VIEWING QUICK REFERENCE")
        
        print_section("QUICK START")
        print("1. See what logs are available:")
        print_example("scionpathml logs", "Overview of all log categories")
        
        print("\n2. Check recent pipeline activity:")
        print_example("scionpathml logs pipeline", "Last 30 lines of pipeline.log")
        print_example("scionpathml logs pipeline --all", "Complete pipeline.log with pagination")
        
        print("\n3. Browse specific measurement logs:")
        print_example("scionpathml logs bandwidth", "List all bandwidth log files")
        
        print("\n4. View specific files:")
        print_example("scionpathml view-log bandwidth", "View first bandwidth file (DEFAULT)")
        print_example("scionpathml view-log bandwidth 1", "View file #1 (last 50 lines)")
        print_example("scionpathml view-log bandwidth latest", "View latest file (highest number)")
        print_example("scionpathml view-log bandwidth latest --all", "View complete latest file")
        
        print_section("FILE SELECTION BEHAVIOR")
        print("• No file specified = first file in list - DEFAULT")
        print_example("scionpathml view-log bandwidth", "Shows first bandwidth file (script_duration.log)")
        print("• Specific number = that file")
        print_example("scionpathml view-log bandwidth 3", "Shows bandwidth file #3")
        print("• 'latest' keyword = highest numbered file")
        print_example("scionpathml view-log bandwidth latest", "Shows highest numbered bandwidth file")