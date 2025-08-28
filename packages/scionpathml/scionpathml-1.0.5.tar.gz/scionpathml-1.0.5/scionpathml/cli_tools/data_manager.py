#Core data management logic and file operations
import os
import json
import shutil
import glob
from pathlib import Path
from datetime import datetime
import re
from .cli_utils import print_error, print_success, print_info, print_example, print_header, print_section, Colors
from scionpathml.cli_tools.path_utils import data_dir

class DataManager:
    """Manage JSON data files in the Data directory structure"""

    def __init__(self):
        self.base_data_path = data_dir() 
        self.archive_path = self.base_data_path / "Archive"
        self.currently_path = self.base_data_path / "Currently"
        self.history_path = self.base_data_path / "History"
        
        # Ensure directories exist
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.currently_path.mkdir(parents=True, exist_ok=True)
        self.history_path.mkdir(parents=True, exist_ok=True)
        
        # File patterns for different measurement types
        self.file_patterns = {
            "Showpaths": r"AS-\d+_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}_\d+-ffaa.*\.json",
            "Bandwidth": r"BW_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}_AS_\d+-ffaa.*\.json", 
            "Comparer": r"delta_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}_\d+-ffaa.*\.json",
            "Prober": r"prober_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}_\d+-ffaa.*\.json",
            "Traceroute": r"TR_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}_AS_\d+-ffaa.*\.json",
            "MP-Prober": r"mp-prober_\d{4}-\d{2}-\d{2}T\d{2}:\d{2}_\d+-ffaa.*\.json",
            "MP-Bandwidth": r"BW-P_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}_AS_\d+-ffaa.*\.json"
        }
        
        # Measurement categories
        self.categories = list(self.file_patterns.keys())
    
    def identify_file_category(self, filename):
        """Identify which category a file belongs to based on its name pattern"""
        for category, pattern in self.file_patterns.items():
            if re.match(pattern, filename):
                return category
        return "Unknown"
    
    def interactive_main_browser(self):
        """Interactive browser for all main directories"""
        print_header("INTERACTIVE DATA BROWSER")
        
        while True:
            # Clear screen for better UX
            os.system('clear' if os.name == 'posix' else 'cls')
            print_header("INTERACTIVE DATA BROWSER")
            
            # Show available directories
            paths_info = self.get_data_paths_info()
            print_section("Available Directories")
            
            valid_dirs = []
            for i, (path_name, info) in enumerate(paths_info.items(), 1):
                if info['exists']:
                    status = "[OK]" if info['total_files'] > 0 else "[EMPTY]"
                    print(f"{i}. {status} {path_name:<12} ({info['total_files']} files, {info['size_mb']:.1f} MB)")
                    valid_dirs.append((path_name, info))
                else:
                    print(f"{i}. [FAIL] {path_name:<12} (not found)")
                    valid_dirs.append((path_name, None))
            
            print()
            print("Commands:")
            print("0. Exit browser")
            print("h. Help")
            print("e. Enter external path")
            print()
            
            try:
                choice = input("Select directory (number/name) or command: ").strip()
                
                if choice == '0' or choice.lower() == 'exit':
                    break
                elif choice.lower() == 'h' or choice.lower() == 'help':
                    self._show_browser_help()
                    input("Press Enter to continue...")
                    continue
                elif choice.lower() == 'e' or choice.lower() == 'external':
                    ext_path = input("Enter external path: ").strip()
                    if ext_path and os.path.exists(ext_path):
                        self.interactive_directory_browser(ext_path)
                    else:
                        print_error("Path not found or invalid")
                        input("Press Enter to continue...")
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(valid_dirs):
                        dir_name, info = valid_dirs[idx]
                        if info and info['exists']:
                            self.interactive_directory_browser(dir_name)
                        else:
                            print_error(f"Directory {dir_name} does not exist")
                            input("Press Enter to continue...")
                    else:
                        print_error("Invalid selection")
                        input("Press Enter to continue...")
                elif choice.lower() in ['archive', 'currently', 'history']:
                    self.interactive_directory_browser(choice)
                else:
                    # Try as external path
                    if os.path.exists(choice):
                        self.interactive_directory_browser(choice)
                    else:
                        print_error("Invalid selection or path not found")
                        input("Press Enter to continue...")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print_error(f"Error: {e}")
                input("Press Enter to continue...")
        
        return True
    
    def interactive_directory_browser(self, directory_name):
        """Interactive browser for a specific directory"""
        target_path = self._get_directory_path(directory_name)
        
        if not target_path:
            # Try as external path
            target_path = Path(directory_name)
            if not target_path.exists():
                print_error(f"Directory not found: {directory_name}")
                return False
        
        current_path = target_path
        navigation_stack = []
        
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
            print_header(f"BROWSING: {current_path}")
            
            if not current_path.exists():
                print_error(f"Directory does not exist: {current_path}")
                input("Press Enter to go back...")
                if navigation_stack:
                    current_path = navigation_stack.pop()
                else:
                    break
                continue
            
            # Get directory contents
            try:
                subdirs = [d for d in current_path.iterdir() if d.is_dir()]
                json_files = list(current_path.glob("*.json"))
            except PermissionError:
                print_error("Permission denied to read this directory")
                input("Press Enter to go back...")
                if navigation_stack:
                    current_path = navigation_stack.pop()
                else:
                    break
                continue
            
            # Show navigation info
            print_info(f"Current: {current_path.absolute()}")
            if navigation_stack:
                print_info(f"Parent: {navigation_stack[-1] if navigation_stack else 'Root'}")
            print()
            
            items = []
            item_count = 0
            
            # Show parent directory option if we can go back
            if navigation_stack:
                item_count += 1
                print(f"{item_count}. (Parent directory)")
                items.append(("parent", navigation_stack[-1]))
            
            # Show subdirectories
            if subdirs:
                print_section(f" Subdirectories ({len(subdirs)})")
                for subdir in sorted(subdirs):
                    item_count += 1
                    subdir_files = list(subdir.glob("*.json"))
                    print(f"{item_count}. Subdirectorie {subdir.name} ({len(subdir_files)} JSON files)")
                    items.append(("directory", subdir))
            
            # Show JSON files with pagination
            if json_files:
                print_section(f"JSON Files ({len(json_files)})")
                
                # Group files by category
                file_groups = {}
                for json_file in json_files:
                    category = self.identify_file_category(json_file.name)
                    if category not in file_groups:
                        file_groups[category] = []
                    file_groups[category].append(json_file)
                
                # Show files by category (first 20 files total)
                files_shown = 0
                max_files_to_show = 20
                
                for category in sorted(file_groups.keys()):
                    if files_shown >= max_files_to_show:
                        break
                        
                    category_files = sorted(file_groups[category], 
                                          key=lambda x: x.stat().st_mtime, reverse=True)
                    
                    print(f"\n   [CATEGORY] {category} ({len(category_files)} files):")
                    
                    for json_file in category_files[:min(5, max_files_to_show - files_shown)]:
                        item_count += 1
                        file_size = json_file.stat().st_size / 1024  # KB
                        modified = datetime.fromtimestamp(json_file.stat().st_mtime)
                        print(f"{item_count}. [FILE] {json_file.name}")
                        print(f"      ({file_size:.1f} KB, {modified.strftime('%Y-%m-%d %H:%M')})")
                        items.append(("file", json_file))
                        files_shown += 1
                        
                        if files_shown >= max_files_to_show:
                            break
                    
                    if len(category_files) > 5:
                        remaining = len(category_files) - min(5, max_files_to_show - files_shown + 5)
                        if remaining > 0:
                            print(f"      ... and {remaining} more {category} files")
                
                if len(json_files) > max_files_to_show:
                    print(f"\n   File ... and {len(json_files) - files_shown} more files")
                    print("       Use 'l' to list all files or 's' to search")
            
            # Show commands
            print_section("Commands")
            print("l. List all files in current directory")
            print("s. Search files in current directory")
            print("i. Directory information/statistics")
            print("r. Refresh current view")
            print("0. Exit browser")
            print("b. Back to main browser")
            print("h. Help")
            print()
            
            try:
                choice = input("Select item (number) or command: ").strip()
                
                if choice == '0' or choice.lower() == 'exit':
                    break
                elif choice.lower() == 'b' or choice.lower() == 'back':
                    return True
                elif choice.lower() == 'h' or choice.lower() == 'help':
                    self._show_browser_help()
                    input("Press Enter to continue...")
                elif choice.lower() == 'r' or choice.lower() == 'refresh':
                    continue  # Just refresh the current view
                elif choice.lower() == 'l' or choice.lower() == 'list':
                    self._show_all_files_in_directory(current_path)
                elif choice.lower() == 's' or choice.lower() == 'search':
                    self._interactive_search_in_directory(current_path)
                elif choice.lower() == 'i' or choice.lower() == 'info':
                    self._show_directory_statistics(current_path)
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(items):
                        item_type, item_path = items[idx]
                        
                        if item_type == "parent":
                            current_path = navigation_stack.pop()
                        elif item_type == "directory":
                            navigation_stack.append(current_path)
                            current_path = item_path
                        elif item_type == "file":
                            self._show_file_details(item_path)
                    else:
                        print_error("Invalid selection")
                        input("Press Enter to continue...")
                else:
                    print_error("Invalid command")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                break
            except ValueError:
                print_error("Please enter a valid number or command")
                input("Press Enter to continue...")
            except Exception as e:
                print_error(f"Error: {e}")
                input("Press Enter to continue...")
        
        return True
    
    def _show_file_details(self, file_path):
        """Show detailed information about a specific file"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print_header(f"FILE DETAILS: {file_path.name}")
        
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            created = datetime.fromtimestamp(stat.st_ctime)
            
            print_info(f"Path: {file_path.absolute()}")
            print_info(f"Category: {self.identify_file_category(file_path.name)}")
            print_info(f"Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print_info(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print_info(f"Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            while True:
                print("Actions:")
                print("1. View file content (first 50 lines)")
                print("2. View file content (all)")
                print("3. View raw JSON structure")
                print("4. Search within file")
                print("5. Copy file path")
                print("0. Back to directory")
                print()
                
                action = input("Choose action: ").strip()
                
                if action == '0':
                    break
                elif action == '1':
                    self._show_file_content(file_path, max_lines=50)
                elif action == '2':
                    self._show_file_content(file_path, max_lines=None)
                elif action == '3':
                    self._show_json_structure(file_path)
                elif action == '4':
                    self._search_within_file(file_path)
                elif action == '5':
                    self._copy_path_to_clipboard(file_path)
                else:
                    print_error("Invalid action")
                    input("Press Enter to continue...")
                    
        except Exception as e:
            print_error(f"Error reading file details: {e}")
            input("Press Enter to continue...")
    
    def _show_file_content(self, file_path, max_lines=None):
        """Show content of a JSON file"""
        os.system('clear' if os.name == 'posix' else 'cls')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse and pretty-print JSON
            try:
                data = json.loads(content)
                pretty_content = json.dumps(data, indent=2, ensure_ascii=False)
                lines = pretty_content.split('\n')
            except json.JSONDecodeError:
                lines = content.split('\n')
            
            print_header(f"CONTENT: {file_path.name}")
            
            if max_lines and len(lines) > max_lines:
                print_info(f"Showing first {max_lines} lines of {len(lines)} total lines")
                display_lines = lines[:max_lines]
                truncated = True
            else:
                display_lines = lines
                truncated = False
            
            print("-" * 80)
            for i, line in enumerate(display_lines, 1):
                print(f"{i:4d}: {line}")
            
            if truncated:
                print(f"... ({len(lines) - max_lines} more lines)")
            
            print("-" * 80)
            print_info(f"Total lines: {len(lines)}, File size: {len(content)} characters")
            
        except Exception as e:
            print_error(f"Error reading file: {e}")
        
        input("\nPress Enter to continue...")
    
    def _show_json_structure(self, file_path):
        """Show JSON structure/schema of the file"""
        os.system('clear' if os.name == 'posix' else 'cls')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print_header(f"JSON STRUCTURE: {file_path.name}")
            
            def analyze_structure(obj, indent=0):
                prefix = "  " * indent
                
                if isinstance(obj, dict):
                    print(f"{prefix} Object ({len(obj)} keys):")
                    for key, value in obj.items():
                        print(f"{prefix}  [KEY] {key}: {type(value).__name__}", end="")
                        if isinstance(value, (list, dict)):
                            if isinstance(value, list) and value:
                                print(f" (length: {len(value)})")
                                if indent < 2:  # Limit recursion depth
                                    analyze_structure(value[0], indent + 2)
                            elif isinstance(value, dict):
                                print(f" ({len(value)} keys)")
                                if indent < 2:
                                    analyze_structure(value, indent + 2)
                            else:
                                print()
                        else:
                            if isinstance(value, str) and len(str(value)) > 50:
                                print(f" ('{str(value)[:50]}...')")
                            else:
                                print(f" ({value})")
                
                elif isinstance(obj, list):
                    print(f"{prefix}Array (length: {len(obj)})")
                    if obj and indent < 2:
                        print(f"{prefix}  Sample item:")
                        analyze_structure(obj[0], indent + 2)
                
                else:
                    print(f"{prefix}[DATA] {type(obj).__name__}: {obj}")
            
            analyze_structure(data)
            
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON format: {e}")
        except Exception as e:
            print_error(f"Error analyzing JSON structure: {e}")
        
        input("\nPress Enter to continue...")
    
    def _search_within_file(self, file_path):
        """Search for text within a file"""
        try:
            search_term = input("Enter search term: ").strip()
            if not search_term:
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            matches = []
            for i, line in enumerate(lines, 1):
                if search_term.lower() in line.lower():
                    matches.append((i, line.strip()))
            
            os.system('clear' if os.name == 'posix' else 'cls')
            print_header(f"SEARCH RESULTS in {file_path.name}")
            
            if matches:
                print_success(f"Found {len(matches)} matches for '{search_term}':")
                print()
                for line_num, line_content in matches[:20]:  # Show first 20 matches
                    # Highlight search term
                    highlighted_line = line_content.replace(
                    search_term, f"{Colors.YELLOW}{search_term}{Colors.END}"
                    )
                    print(f"{line_num:4d}: {highlighted_line}")
                
                if len(matches) > 20:
                    print(f"\n... and {len(matches) - 20} more matches")
                else:
                    print_error(f"No matches found for '{search_term}'")
                
        except Exception as e:
            print_error(f"Error searching file: {e}")
        
        input("\nPress Enter to continue...")
    
    def _copy_path_to_clipboard(self, file_path):
        """Copy file path to clipboard (if possible)"""
        try:
            import subprocess
            path_str = str(file_path.absolute())
            
            # Try to copy to clipboard based on OS
            try:
                if os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xclip', '-selection', 'clipboard'], 
                                 input=path_str.encode(), check=True)
                elif os.name == 'nt':  # Windows
                    subprocess.run(['clip'], input=path_str.encode(), check=True)
                
                print_success(f"Path copied to clipboard: {path_str}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_info(f"Copy manually: {path_str}")
                
        except ImportError:
            print_info(f"Copy manually: {file_path.absolute()}")
        
        input("Press Enter to continue...")
    
    def _show_all_files_in_directory(self, directory_path):
        """Show all files in directory with pagination"""
        try:
            json_files = list(directory_path.glob("*.json"))
            
            if not json_files:
                print_info("No JSON files found in this directory")
                input("Press Enter to continue...")
                return
            
            # Sort by modification time (newest first)
            json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            page_size = 20
            current_page = 0
            total_pages = (len(json_files) + page_size - 1) // page_size
            
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                print_header(f"ALL FILES IN {directory_path.name}")
                
                start_idx = current_page * page_size
                end_idx = min(start_idx + page_size, len(json_files))
                page_files = json_files[start_idx:end_idx]
                
                print(f"\nPage {current_page + 1} of {total_pages} ({len(json_files)} total files)")
                print("-" * 80)
                
                for i, json_file in enumerate(page_files, start_idx + 1):
                    stat = json_file.stat()
                    size_kb = stat.st_size / 1024
                    modified = datetime.fromtimestamp(stat.st_mtime)
                    category = self.identify_file_category(json_file.name)
                    
                    print(f"{i:3d}. [FILE] {json_file.name}")
                    print(f"     [INFO] {category} | {size_kb:.1f} KB | {modified.strftime('%Y-%m-%d %H:%M')}")
                
                print("-" * 80)
                print("n. Next page | p. Previous page | q. Quit | [number]. View file")
                
                choice = input("Command: ").strip().lower()
                
                if choice == 'q' or choice == 'quit':
                    break
                elif choice == 'n' or choice == 'next':
                    if current_page < total_pages - 1:
                        current_page += 1
                    else:
                        print_info("Already on last page")
                        input("Press Enter to continue...")
                elif choice == 'p' or choice == 'prev':
                    if current_page > 0:
                        current_page -= 1
                    else:
                        print_info("Already on first page")
                        input("Press Enter to continue...")
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(json_files):
                        self._show_file_details(json_files[idx])
                    else:
                        print_error("Invalid file number")
                        input("Press Enter to continue...")
                
        except Exception as e:
            print_error(f"Error listing files: {e}")
            input("Press Enter to continue...")
    
    def _interactive_search_in_directory(self, directory_path):
        """Interactive search within a directory"""
        pattern = input("Enter search pattern: ").strip()
        if not pattern:
            return
        
        try:
            matching_files = list(directory_path.glob(f"*{pattern}*.json"))
            
            if not matching_files:
                print_error(f"No files found matching '*{pattern}*'")
                input("Press Enter to continue...")
                return
            
            os.system('clear' if os.name == 'posix' else 'cls')
            print_header(f"SEARCH RESULTS: {pattern}")
            print_success(f"Found {len(matching_files)} files:")
            print()
            
            for i, file_path in enumerate(matching_files, 1):
                stat = file_path.stat()
                size_kb = stat.st_size / 1024
                modified = datetime.fromtimestamp(stat.st_mtime)
                category = self.identify_file_category(file_path.name)
                
                print(f"{i}. [FILE] {file_path.name}")
                print(f"   [INFO] {category} | {size_kb:.1f} KB | {modified.strftime('%Y-%m-%d %H:%M')}")
            
            print("\nSelect file number to view details, or press Enter to continue...")
            choice = input("File number: ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(matching_files):
                    self._show_file_details(matching_files[idx])
                    
        except Exception as e:
            print_error(f"Error searching: {e}")
            input("Press Enter to continue...")
    
    def _show_directory_statistics(self, directory_path):
        """Show detailed statistics about a directory"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print_header(f"DIRECTORY STATISTICS: {directory_path.name}")
        
        try:
            all_files = list(directory_path.rglob("*.json"))
            
            if not all_files:
                print_info("No JSON files found")
                input("Press Enter to continue...")
                return
            
            # Calculate statistics
            total_size = sum(f.stat().st_size for f in all_files)
            newest_file = max(all_files, key=lambda x: x.stat().st_mtime)
            oldest_file = min(all_files, key=lambda x: x.stat().st_mtime)
            
            newest_time = datetime.fromtimestamp(newest_file.stat().st_mtime)
            oldest_time = datetime.fromtimestamp(oldest_file.stat().st_mtime)
            
            print_info(f"Path: {directory_path.absolute()}")
            print_info(f"Total files: {len(all_files)}")
            print_info(f"Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
            print_info(f"Newest: {newest_file.name} ({newest_time.strftime('%Y-%m-%d %H:%M')})")
            print_info(f"Oldest: {oldest_file.name} ({oldest_time.strftime('%Y-%m-%d %H:%M')})")
            
            # Show breakdown by category
            category_stats = {}
            for file_path in all_files:
                category = self.identify_file_category(file_path.name)
                if category not in category_stats:
                    category_stats[category] = {'count': 0, 'size': 0}
                category_stats[category]['count'] += 1
                category_stats[category]['size'] += file_path.stat().st_size
            
            print_section("Breakdown by Category")
            for category, stats in sorted(category_stats.items()):
                size_mb = stats['size'] / 1024 / 1024
                print(f"   [STATS] {category:<20} {stats['count']:>4} files ({size_mb:>6.1f} MB)")
                
        except Exception as e:
            print_error(f"Error calculating statistics: {e}")
        
        input("\nPress Enter to continue...")
    
    def _show_browser_help(self):
        """Show help for the interactive browser"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print_header("INTERACTIVE BROWSER HELP")
        
        print_section("Navigation")
        print("• Use numbers to select directories or files")
        print("• Use 'b' or 'back' to return to main browser")
        print("• Use '0' or 'exit' to quit")
        print("• Use '..' or parent option to go up one level")
        
        print_section("Commands")
        print("• l - List all files in current directory (paginated)")
        print("• s - Search for files in current directory")
        print("• i - Show directory information and statistics")
        print("• r - Refresh current view")
        print("• h - Show this help")
        print("• e - Enter external path (main browser only)")
        
        print_section("File Actions")
        print("• View file content (with line numbers)")
        print("• Analyze JSON structure")
        print("• Search within file content")
        print("• Copy file path to clipboard")
        
        print_section("Tips")
        print("• Files are automatically categorized by naming patterns")
        print("• Use Ctrl+C to quickly exit at any time")
        print("• Large files show only first 50 lines by default")
        print("• File listing is paginated for better performance")
        print("• Search is case-insensitive")
        print("• Screen clears for better viewing experience")
        
    # Original DataManager methods below
    
    def get_data_paths_info(self):
        """Get information about all data paths"""
        paths_info = {}
        
        for main_path in [self.archive_path, self.currently_path, self.history_path]:
            if main_path.exists():
                # Get all JSON files in main directory and subdirectories
                all_json_files = list(main_path.rglob("*.json"))
                
                # Categorize files by pattern and location
                main_files = list(main_path.glob("*.json"))
                category_counts = {}
                pattern_counts = {}
                
                # Count files by category directories
                for category in self.categories:
                    category_path = main_path / category
                    if category_path.exists():
                        cat_files = list(category_path.glob("*.json"))
                        category_counts[category] = len(cat_files)
                    else:
                        category_counts[category] = 0
                
                # Count files by pattern (including main directory)
                for category in self.categories:
                    pattern_counts[category] = 0
                
                for json_file in all_json_files:
                    file_category = self.identify_file_category(json_file.name)
                    if file_category in pattern_counts:
                        pattern_counts[file_category] += 1
                    else:
                        pattern_counts["Unknown"] = pattern_counts.get("Unknown", 0) + 1
                
                total_category_files = sum(category_counts.values())
                
                paths_info[main_path.name] = {
                    'path': str(main_path),
                    'exists': True,
                    'main_files': len(main_files),
                    'category_files': total_category_files,
                    'total_files': len(all_json_files),
                    'categories': category_counts,
                    'patterns': pattern_counts,
                    'size_mb': self._get_directory_size(main_path)
                }
            else:
                paths_info[main_path.name] = {
                    'path': str(main_path),
                    'exists': False,
                    'main_files': 0,
                    'category_files': 0,
                    'total_files': 0,
                    'categories': {},
                    'patterns': {},
                    'size_mb': 0
                }
        
        return paths_info
    
    def show_data_overview(self):
        """Show overview of all data directories"""
        print_header("DATA DIRECTORY OVERVIEW")
        
        paths_info = self.get_data_paths_info()
        total_files = 0
        total_size = 0
        
        for path_name, info in paths_info.items():
            if info['exists']:
                status = "[OK]" if info['total_files'] > 0 else "[EMPTY]"
                print(f"{status} {path_name:<12} {info['total_files']:>6} files ({info['size_mb']:>8.1f} MB)")
                total_files += info['total_files']
                total_size += info['size_mb']
            else:
                print(f"[MISSING] {path_name:<12}      0 files (not found)")
        
        print()
        print_success(f"Total: {total_files} JSON files ({total_size:.1f} MB)")
        
        print()
        print_info("Usage:")
        print_example("scionpathml data-show Archive", "Show detailed Archive contents")
        print_example("scionpathml data-show Archive --interactive", "Browse Archive interactively")
        print_example("scionpathml data-browse", "Interactive browser for all directories")
        print_example("scionpathml data-move Archive Currently", "Move Archive to Currently")
        print_example("scionpathml data-move Archive /custom/path", "Move Archive to external path")
    
    def show_directory_details(self, directory_name):
        """Show detailed contents of a specific directory"""
        target_path = self._get_directory_path(directory_name)
        
        if not target_path:
            # Try as external path
            target_path = Path(directory_name)
            if not target_path.exists():
                print_error(f"Directory not found: {directory_name}")
                return False
        
        if not target_path.exists():
            print_error(f"Directory does not exist: {target_path}")
            return False
        
        print_header(f"{directory_name.upper()} DIRECTORY DETAILS")
        print_info(f"Path: {target_path.absolute()}")
        
        # Get all JSON files
        all_files = list(target_path.rglob("*.json"))
        main_files = list(target_path.glob("*.json"))
        
        if not all_files:
            print_error("No JSON files found in this directory")
            return True
        
        # Show files by pattern/category
        print_section(f"Files by Measurement Type ({len(all_files)} total)")
        
        pattern_groups = {}
        for json_file in all_files:
            category = self.identify_file_category(json_file.name)
            if category not in pattern_groups:
                pattern_groups[category] = []
            pattern_groups[category].append(json_file)
        
        for category in sorted(pattern_groups.keys()):
            files_list = pattern_groups[category]
            if files_list:
                total_size = sum(f.stat().st_size for f in files_list) / 1024  # KB
                latest_file = max(files_list, key=lambda x: x.stat().st_mtime)
                latest_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                
                print(f"  Category {category:<20} {len(files_list):>4} files ({total_size:>8.1f} KB) - Latest: {latest_time.strftime('%Y-%m-%d %H:%M')}")
                
                # Show sample files
                if len(files_list) <= 3:
                    for file_path in sorted(files_list, key=lambda x: x.stat().st_mtime, reverse=True):
                        rel_path = file_path.relative_to(target_path)
                        size_kb = file_path.stat().st_size / 1024
                        modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                        print(f"      File {rel_path} ({size_kb:.1f} KB) - {modified.strftime('%Y-%m-%d %H:%M')}")
                else:
                    # Show latest 2 files
                    sorted_files = sorted(files_list, key=lambda x: x.stat().st_mtime, reverse=True)
                    for file_path in sorted_files[:2]:
                        rel_path = file_path.relative_to(target_path)
                        size_kb = file_path.stat().st_size / 1024
                        modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                        print(f"      File {rel_path} ({size_kb:.1f} KB) - {modified.strftime('%Y-%m-%d %H:%M')}")
                    print(f"      ... and {len(files_list) - 2} more files")
                print()
        
        # Show directory structure
        subdirs = [d for d in target_path.iterdir() if d.is_dir()]
        if subdirs:
            print_section("Subdirectories")
            for subdir in sorted(subdirs):
                subdir_files = list(subdir.glob("*.json"))
                print(f"Subdirectories {subdir.name:<20} ({len(subdir_files)} files)")
        
        return True
    
    def move_data(self, source_dir, destination, category=None, confirm=True):
        """Move data from source to destination (can be internal directory or external path)"""
        # Determine if destination is internal directory or external path
        if destination.lower() in ['archive', 'currently', 'history']:
            # Internal move
            dest_path = self._get_directory_path(destination)
            if not dest_path:
                print_error("Invalid destination directory")
                return False
            external_move = False
            dest_description = destination
        else:
            # External move
            dest_path = Path(destination)
            external_move = True
            dest_description = f"external path: {destination}"
        
        # Validate source directory
        source_path = self._get_directory_path(source_dir)
        if not source_path:
            print_error("Invalid source directory")
            print_error("Valid directories: Archive, Currently, History")
            return False
        
        if not source_path.exists():
            print_error(f"Source directory does not exist: {source_path}")
            return False
        
        # Create destination if it doesn't exist
        try:
            dest_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print_error(f"Cannot create destination directory: {e}")
            return False
        
        # Determine what to move
        if category:
            if category not in self.categories:
                print_error(f"Invalid category: {category}")
                print_error(f"Valid categories: {', '.join(self.categories)}")
                return False
            
            # Find files by pattern and category directory
            files_to_move = []
            
            # Files in category subdirectory
            category_path = source_path / category
            if category_path.exists():
                files_to_move.extend(list(category_path.glob("*.json")))
            
            # Files in main directory matching pattern
            pattern = self.file_patterns.get(category)
            if pattern:
                all_main_files = list(source_path.glob("*.json"))
                for file_path in all_main_files:
                    if re.match(pattern, file_path.name):
                        files_to_move.append(file_path)
            
            # Remove duplicates
            files_to_move = list(set(files_to_move))
            move_description = f"{category} files from {source_dir}"
        else:
            # Move all files
            files_to_move = list(source_path.rglob("*.json"))
            move_description = f"all files from {source_dir}"
        
        if not files_to_move:
            print_error(f"No JSON files found to move from {source_path}")
            return False
        
        print_header(f"MOVE DATA: {source_dir} → {dest_description}")
        print_info(f"Found {len(files_to_move)} JSON files to move")
        
        # Show what will be moved by category
        move_groups = {}
        for file_path in files_to_move:
            file_category = self.identify_file_category(file_path.name)
            if file_category not in move_groups:
                move_groups[file_category] = []
            move_groups[file_category].append(file_path)
        
        print_section("Files to Move by Type")
        for cat, files_list in sorted(move_groups.items()):
            total_size = sum(f.stat().st_size for f in files_list) / 1024  # KB
            print(f"Move {cat:<20} {len(files_list):>4} files ({total_size:>8.1f} KB)")
        
        # Confirm move
        if confirm:
            print()
            move_type = "external location" if external_move else f"{destination} directory"
            response = input(f"Move {len(files_to_move)} files to {move_type}? (y/N): ")
            if response.lower() != 'y':
                print_info("Move cancelled")
                return False
        
        # Perform move
        moved_count = 0
        failed_count = 0
        
        for file_path in files_to_move:
            try:
                if external_move:
                    # For external moves, preserve relative structure from main directory
                    if file_path.parent == source_path:
                        # File is in main directory
                        dest_file_path = dest_path / file_path.name
                    else:
                        # File is in subdirectory, preserve structure
                        relative_path = file_path.relative_to(source_path)
                        dest_file_path = dest_path / relative_path
                else:
                    # For internal moves, preserve full directory structure
                    relative_path = file_path.relative_to(source_path)
                    dest_file_path = dest_path / relative_path
                
                # Create destination subdirectory if needed
                dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(file_path), str(dest_file_path))
                moved_count += 1
                
            except Exception as e:
                print_error(f"Failed to move {file_path.name}: {e}")
                failed_count += 1
        
        # Clean up empty directories in source
        if not external_move:  # Only cleanup for internal moves
            self._cleanup_empty_directories(source_path)
        
        if moved_count > 0:
            print_success(f"Successfully moved {moved_count} files to {dest_description}")
        if failed_count > 0:
            print_error(f"Failed to move {failed_count} files")
        
        return moved_count > 0
    
    def delete_data(self, directory_name, category=None, confirm=True):
        """Delete data from specified directory"""
        target_path = self._get_directory_path(directory_name)
        if not target_path:
            print_error(f"Invalid directory: {directory_name}")
            return False
        
        if not target_path.exists():
            print_error(f"Directory does not exist: {target_path}")
            return False
        
        # Determine what to delete
        if category:
            if category not in self.categories:
                print_error(f"Invalid category: {category}")
                print_error(f"Valid categories: {', '.join(self.categories)}")
                return False
            
            # Find files by pattern and category directory
            files_to_delete = []
            
            # Files in category subdirectory
            category_path = target_path / category
            if category_path.exists():
                files_to_delete.extend(list(category_path.glob("*.json")))
            
            # Files in main directory matching pattern
            pattern = self.file_patterns.get(category)
            if pattern:
                all_main_files = list(target_path.glob("*.json"))
                for file_path in all_main_files:
                    if re.match(pattern, file_path.name):
                        files_to_delete.append(file_path)
            
            # Remove duplicates
            files_to_delete = list(set(files_to_delete))
            delete_description = f"{category} files in {directory_name}"
        else:
            files_to_delete = list(target_path.rglob("*.json"))
            delete_description = f"all files in {directory_name}"
        
        if not files_to_delete:
            print_error(f"No JSON files found in {target_path}")
            return False
        
        print_header(f"DELETE DATA FROM {directory_name.upper()}")
        print_info(f"Found {len(files_to_delete)} JSON files to delete")
        
        # Show what will be deleted by category
        delete_groups = {}
        for file_path in files_to_delete:
            file_category = self.identify_file_category(file_path.name)
            if file_category not in delete_groups:
                delete_groups[file_category] = []
            delete_groups[file_category].append(file_path)
        
        print_section("Files to Delete by Type")
        total_size_mb = 0
        for cat, files_list in sorted(delete_groups.items()):
            total_size = sum(f.stat().st_size for f in files_list)
            total_size_kb = total_size / 1024
            total_size_mb += total_size / 1024 / 1024
            print(f"Remove {cat:<20} {len(files_list):>4} files ({total_size_kb:>8.1f} KB)")
        
        print()
        print_info(f"Total size to delete: {total_size_mb:.1f} MB")
        
        # Confirm deletion
        if confirm:
            print()
            print(f"{Colors.RED}WARNING: This action cannot be undone!{Colors.END}")
            response = input(f"Delete {len(files_to_delete)} files from {directory_name}? (y/N): ")
            if response.lower() != 'y':
                print_info("Deletion cancelled")
                return False
        
        # Perform deletion
        deleted_count = 0
        failed_count = 0
        
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                print_error(f"Failed to delete {file_path.name}: {e}")
                failed_count += 1
        
        # Clean up empty directories
        self._cleanup_empty_directories(target_path)
        
        if deleted_count > 0:
            print_success(f"Successfully deleted {deleted_count} files")
        if failed_count > 0:
            print_error(f"Failed to delete {failed_count} files")
        
        return deleted_count > 0
    
    def search_files(self, pattern, directory_name=None):
        """Search for files matching pattern"""
        print_header("SEARCH JSON FILES")
        
        if directory_name:
            if directory_name.lower() in ['archive', 'currently', 'history']:
                search_path = self._get_directory_path(directory_name)
                if not search_path or not search_path.exists():
                    print_error(f"Directory not found: {directory_name}")
                    return []
                search_paths = [search_path]
                search_desc = f"in {directory_name}"
            else:
                # External path
                search_path = Path(directory_name)
                if not search_path.exists():
                    print_error(f"Path not found: {directory_name}")
                    return []
                search_paths = [search_path]
                search_desc = f"in {directory_name}"
        else:
            search_paths = [self.archive_path, self.currently_path, self.history_path]
            search_desc = "in all directories"
        
        print_info(f"Searching for '*{pattern}*' {search_desc}")
        
        found_files = []
        for search_path in search_paths:
            if search_path.exists():
                # Search in main directory and subdirectories
                pattern_files = list(search_path.rglob(f"*{pattern}*.json"))
                for file_path in pattern_files:
                    file_category = self.identify_file_category(file_path.name)
                    found_files.append({
                        'path': file_path,
                        'relative_path': file_path.relative_to(search_path) if search_path in [self.archive_path, self.currently_path, self.history_path] else file_path.name,
                        'category': file_category,
                        'size_kb': file_path.stat().st_size / 1024,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'search_root': search_path.name if search_path in [self.archive_path, self.currently_path, self.history_path] else str(search_path)
                    })
        
        if not found_files:
            print_error(f"No files found matching '*{pattern}*'")
            return []
        
        # Sort by modification time (newest first)
        found_files.sort(key=lambda x: x['modified'], reverse=True)
        
        print_success(f"Found {len(found_files)} files:")
        print()
        
        # Group by category for better display
        category_groups = {}
        for file_info in found_files:
            cat = file_info['category']
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(file_info)
        
        for category in sorted(category_groups.keys()):
            files_list = category_groups[category]
            print_section(f"{category} Files ({len(files_list)})")
            
            for i, file_info in enumerate(files_list[:10]):  # Show first 10 per category
                mod_time = file_info['modified'].strftime('%Y-%m-%d %H:%M')
                location = f"[{file_info['search_root']}]" if len(search_paths) > 1 else ""
                print(f"    {file_info['relative_path']}")
                print(f"      ({file_info['size_kb']:.1f} KB) - {mod_time} {location}")
                print()
            
            if len(files_list) > 10:
                print(f"   ... and {len(files_list) - 10} more {category} files")
                print()
        
        return found_files
    
    def _get_directory_path(self, directory_name):
        """Get Path object for directory name"""
        if directory_name.lower() == "archive":
            return self.archive_path
        elif directory_name.lower() == "currently":
            return self.currently_path
        elif directory_name.lower() == "history":
            return self.history_path
        else:
            return None
    
    def _get_directory_size(self, directory_path):
        """Get total size of directory in MB"""
        if not directory_path.exists():
            return 0
        
        total_size = 0
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size / 1024 / 1024  # Convert to MB
    
    def _cleanup_empty_directories(self, base_path):
        """Remove empty directories after move/delete operations"""
        for category in self.categories:
            category_path = base_path / category
            if category_path.exists() and not any(category_path.iterdir()):
                try:
                    category_path.rmdir()
                except OSError:
                    pass  # Directory not empty or other issue