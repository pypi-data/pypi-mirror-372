# Log formatting and display utilities
import os
from datetime import datetime

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

class LogDisplay:
    """Handle log display formatting"""
    
    def show_logs_overview(self, log_manager):
        """Display overview of all logs"""
        print_header("SCION LOGS OVERVIEW")
        
        # Show pipeline.log first
        pipeline_info = log_manager.get_pipeline_log_info()
        if pipeline_info:
            modified_str = pipeline_info['modified'].strftime('%Y-%m-%d %H:%M')
            print_success(f" pipeline.log ({pipeline_info['size_kb']:.1f} KB) - {modified_str}")
        else:
            print_error(" pipeline.log (not found)")
        
        print()
        print_section(" LOG CATEGORIES")
        
        category_info = log_manager.get_category_info()
        for category, info in category_info.items():
            if info['exists']:
                status = "[OK]" if info['file_count'] > 0 else "[EMPTY]"
                print(f"{status} {category:<15} ({info['file_count']} files)")
            else:
                print(f"[MISSING] {category:<15} (directory not found)")
        
        print()
        print_info(" Usage:")
        print_example("scionpathml logs pipeline", "View pipeline.log (last 30 lines)")
        print_example("scionpathml logs bandwidth", "Browse bandwidth logs")
        print_example("scionpathml logs pipeline --all", "View entire pipeline.log")
        print_example("scionpathml view-log bandwidth", "View first bandwidth file")
        print_example("scionpathml view-log bandwidth latest", "View latest bandwidth file")
    
    def show_pipeline_log(self, log_manager, show_all=False):
        """Display pipeline.log content with optional --all flag"""
        pipeline_info = log_manager.get_pipeline_log_info()
        if not pipeline_info:
            print_error("pipeline.log not found")
            return
        
        print_header("PIPELINE LOG")
        modified_str = pipeline_info['modified'].strftime('%Y-%m-%d %H:%M')
        print(f" pipeline.log ({pipeline_info['size_kb']:.1f} KB) - Modified: {modified_str}")
        print()
        
        # Read and display content - full file if show_all is True
        lines_to_show = None if show_all else 30
        content = log_manager.read_log_file(pipeline_info['path'], lines=lines_to_show)
        
        if content and 'error' not in content:
            if show_all:
                print_info(f"Showing entire file ({content['total_lines']} lines):")
            else:
                print_info(f"Showing last 30 lines (total: {content['total_lines']} lines):")
            
            print("-" * 80)
            
            # For very large files, add pagination
            if show_all and len(content['lines']) > 100:
                self._show_with_pagination(content['lines'])
            else:
                for line_info in content['lines']:
                    status_prefix = f"[{line_info['status']}]" if line_info['status'] != 'NORMAL' else ""
                    print(f"{line_info['line_number']:>4}: {status_prefix} {line_info['content']}")
            
            if not show_all and content['total_lines'] > 30:
                print()
                print_info(" View entire file:")
                print_example("scionpathml logs pipeline --all", "View complete pipeline.log")
        else:
            error_msg = content.get('error', 'Unknown error') if content else 'Unknown error'
            print_error(f"Error reading pipeline.log: {error_msg}")
    
    def show_category_files(self, log_manager, category):
        """Display files in a category"""
        files = log_manager.get_category_files(category)
        if not files:
            print_error(f"No log files found in {category}")
            return
        
        print_header(f"{category.upper()} LOGS")
        print(f"Found {len(files)} log files (sorted by file number):")
        print("-" * 80)
        
        # List files with numbers
        for i, file_info in enumerate(files, 1):
            modified_str = file_info['modified'].strftime('%Y-%m-%d %H:%M')
            as_info = file_info.get('as_info', '')
            
            # Mark the latest file (highest numbered = last in list)
            latest_marker = " LATEST" if i == len(files) else ""
            
            print(f"{i:>2}. {file_info['filename']:<35} "
                  f"({file_info['size_kb']:>6.1f} KB) "
                  f"{as_info:<20} {modified_str}{latest_marker}")
        
        print()
        print_info(" View a specific file:")
        print_example(f"scionpathml view-log {category}", f"View first file (#{1}) - DEFAULT")
        print_example(f"scionpathml view-log {category} 1", "View file #1")
        print_example(f"scionpathml view-log {category} {len(files)}", f"View file #{len(files)} (latest)")
        print_example(f"scionpathml view-log {category} latest", "View latest file")
        print_example(f"scionpathml view-log {category} latest --all", "View complete latest file")
    
    def show_specific_log(self, log_manager, category, file_selector, show_all=False):
        """Display a specific log file"""
        target_file = log_manager.get_file_by_selector(category, file_selector)
        if not target_file:
            if category.lower() == "pipeline":
                print_error("pipeline.log not found")
            else:
                print_error(f"Could not find file in {category}: {file_selector}")
                print_info(" Available options:")
                print_example(f"scionpathml logs {category}", "See numbered file list")
                print_example(f"scionpathml view-log {category}", "View first file (default)")
                print_example(f"scionpathml view-log {category} latest", "View latest file")
            return
        
        # Get file info
        filename = os.path.basename(target_file)
        stat = os.stat(target_file)
        size_kb = stat.st_size / 1024
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        
        # Determine if this is the first or latest file and show appropriate info
        display_info = ""
        if category.lower() != "pipeline":
            files = log_manager.get_category_files(category)
            if files:
                if target_file == files[0]['path']:  # First file in sorted list
                    if not file_selector:
                        display_info = " (FIRST FILE - DEFAULT)"
                    else:
                        display_info = " (FIRST FILE)"
                elif target_file == files[-1]['path']:  # Last file in sorted list = latest
                    display_info = " (LATEST FILE)"
        
        print_header(f"VIEWING: {filename}")
        print(f" {filename} ({size_kb:.1f} KB) - Modified: {modified}{display_info}")
        print()
        
        # Read content - full file if show_all is True
        lines_to_show = None if show_all else 50
        content = log_manager.read_log_file(target_file, lines=lines_to_show)
        
        if content and 'error' not in content:
            if show_all:
                print_info(f"Showing entire file ({content['total_lines']} lines):")
            else:
                print_info(f"Showing last {content['displayed_lines']} lines (total: {content['total_lines']} lines):")
            
            print("-" * 80)
            
            # For very large files, add pagination
            if show_all and len(content['lines']) > 100:
                self._show_with_pagination(content['lines'])
            else:
                for line_info in content['lines']:
                    status_prefix = f"[{line_info['status']}]" if line_info['status'] != 'NORMAL' else ""
                    print(f"{line_info['line_number']:>4}: {status_prefix} {line_info['content']}")
            
            if not show_all and content['total_lines'] > 50:
                print()
                print_info("View entire file:")
                if category.lower() == "pipeline":
                    print_example("scionpathml view-log pipeline --all", "View complete pipeline.log")
                else:
                    selector_text = file_selector if file_selector else "1"
                    print_example(f"scionpathml view-log {category} {selector_text} --all", "View complete file")
        else:
            error_msg = content.get('error', 'Unknown error') if content else 'Unknown error'
            print_error(f"Error reading log file: {error_msg}")
    
    def _show_with_pagination(self, lines):
        """Show lines with pagination for large files"""
        lines_per_page = 50
        total_pages = (len(lines) + lines_per_page - 1) // lines_per_page
        current_page = 1
        
        while current_page <= total_pages:
            start_idx = (current_page - 1) * lines_per_page
            end_idx = min(start_idx + lines_per_page, len(lines))
            
            print(f"\n{Colors.CYAN}--- Page {current_page}/{total_pages} ---{Colors.END}")
            
            for line_info in lines[start_idx:end_idx]:
                status_prefix = f"[{line_info['status']}]" if line_info['status'] != 'NORMAL' else ""
                print(f"{line_info['line_number']:>4}: {status_prefix} {line_info['content']}")
            
            if current_page < total_pages:
                print(f"\n{Colors.YELLOW}Press Enter for next page, 'q' to quit, or page number (1-{total_pages}):{Colors.END}")
                try:
                    user_input = input().strip().lower()
                    if user_input == 'q':
                        break
                    elif user_input == '':
                        current_page += 1
                    elif user_input.isdigit():
                        page_num = int(user_input)
                        if 1 <= page_num <= total_pages:
                            current_page = page_num
                        else:
                            print_error(f"Invalid page number. Enter 1-{total_pages}")
                    else:
                        current_page += 1
                except KeyboardInterrupt:
                    print("\n")
                    break
            else:
                current_page += 1