#Log file management and parsing
import os
import re
import glob
from datetime import datetime

class SimpleLogManager:
    """Simple log manager for SCION measurement logs"""
    
    def __init__(self, log_dir="Data/Logs/"):
        self.log_dir = log_dir
        self.categories = ["Bandwidth", "Comparer", "MP-Bandwidth", "MP-Prober", 
                          "Prober", "Showpaths", "Traceroute"]
    
    def get_pipeline_log_info(self):
        """Get pipeline.log information"""
        pipeline_log = os.path.join(self.log_dir, "pipeline.log")
        if not os.path.exists(pipeline_log):
            return None
        
        stat = os.stat(pipeline_log)
        return {
            'path': pipeline_log,
            'size_kb': stat.st_size / 1024,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'exists': True
        }
    
    def get_category_info(self):
        """Get information about all log categories"""
        category_info = {}
        
        for category in self.categories:
            cat_path = os.path.join(self.log_dir, category)
            if os.path.exists(cat_path):
                log_files = glob.glob(os.path.join(cat_path, "*.log"))
                category_info[category] = {
                    'exists': True,
                    'file_count': len(log_files),
                    'path': cat_path
                }
            else:
                category_info[category] = {
                    'exists': False,
                    'file_count': 0,
                    'path': cat_path
                }
        
        return category_info
    
    def _extract_file_number(self, filename):
        """Extract numerical part from filename for sorting"""
        # Look for patterns like filename_1.log, filename_2.log, etc.
        match = re.search(r'_(\d+)\.log$', filename)
        if match:
            return int(match.group(1))
        
        # Also check for patterns like 1.log, 2.log, etc.
        match = re.search(r'^(\d+)\.log$', filename)
        if match:
            return int(match.group(1))
        
        # If no number found, treat as 0 for sorting (so script_duration.log comes first)
        return 0
    
    def get_category_files(self, category):
        """Get log files for a specific category, sorted by filename number (0, 1, 2, 3, etc.)"""
        if category.lower() == "pipeline":
            pipeline_info = self.get_pipeline_log_info()
            return [pipeline_info] if pipeline_info else []
        
        category_path = os.path.join(self.log_dir, category.capitalize())
        if not os.path.exists(category_path):
            return []
        
        # Get all log files
        log_files = glob.glob(os.path.join(category_path, "*.log"))
        
        # Sort by filename number (ascending: 0, 1, 2, 3, 4, 5...)
        # Files without numbers (like script_duration.log) get number 0 and come first
        log_files.sort(key=lambda x: self._extract_file_number(os.path.basename(x)))
        
        file_info = []
        for log_file in log_files:
            stat = os.stat(log_file)
            filename = os.path.basename(log_file)
            
            # Extract AS info if available
            as_match = re.search(r'(\d+-[a-f0-9:]+)', filename)
            as_info = as_match.group(1) if as_match else ""
            
            file_info.append({
                'path': log_file,
                'filename': filename,
                'size_kb': stat.st_size / 1024,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'as_info': as_info,
                'file_number': self._extract_file_number(filename)
            })
        
        return file_info
    
    def get_latest_file_in_category(self, category):
        """Get the highest numbered file in a category (latest by sequence number)"""
        files = self.get_category_files(category)
        if not files:
            return None
        
        # Files are sorted by number (ascending), so last file is the latest
        return files[-1]['path']
    
    def get_first_file_in_category(self, category):
        """Get the first file in a category (lowest number or script_duration.log)"""
        files = self.get_category_files(category)
        if not files:
            return None
        
        # Files are sorted by number (ascending), so first file is index 0
        return files[0]['path']
    
    def read_log_file(self, filepath, lines=50):
        """Read log file and return formatted content
        
        Args:
            filepath: Path to the log file
            lines: Number of lines to show from end of file. If None, show entire file.
        """
        if not os.path.exists(filepath):
            return {'error': f'File not found: {filepath}'}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            
            # Determine which lines to display
            if lines is None:
                # Show all lines (--all flag)
                display_lines = all_lines
                start_line = 1
            else:
                # Show last N lines (default behavior)
                display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                start_line = max(1, len(all_lines) - len(display_lines) + 1)
            
            formatted_lines = []
            for i, line in enumerate(display_lines, start=start_line):
                line_content = line.rstrip()
                
                # Determine status based on log level
                line_upper = line_content.upper()
                if any(word in line_upper for word in ['ERROR', 'FAILED', 'EXCEPTION', 'CRITICAL']):
                    status = "ERROR"
                elif any(word in line_upper for word in ['WARNING', 'WARN']):
                    status = "WARNING"
                elif any(word in line_upper for word in ['INFO', 'INFORMATION']):
                    status = "INFO"
                elif any(word in line_upper for word in ['DEBUG', 'TRACE']):
                    status = "DEBUG"
                else:
                    status = "NORMAL"
                
                formatted_lines.append({
                    'line_number': i,
                    'content': line_content,
                    'status': status
                })
            
            return {
                'total_lines': len(all_lines),
                'displayed_lines': len(display_lines),
                'lines': formatted_lines,
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'showing_all': lines is None
            }
            
        except Exception as e:
            return {'error': f'Error reading file: {str(e)}'}
    
    def validate_category(self, category):
        """Check if category is valid"""
        if category.lower() == "pipeline":
            return True
        return category.capitalize() in self.categories
    
    def get_file_by_selector(self, category, selector):
        """Get file path by number or 'latest' or None (defaults to first)"""
        if category.lower() == "pipeline":
            # Pipeline always returns the pipeline.log file
            pipeline_info = self.get_pipeline_log_info()
            return pipeline_info['path'] if pipeline_info else None
        
        files = self.get_category_files(category)
        if not files:
            return None
        
        # Handle None or empty string - default to FIRST file
        if not selector:
            return files[0]['path']  # First file in sorted list
        
        # Handle "latest" - return highest numbered file
        if selector == "latest":
            return files[-1]['path']  # Last file in sorted list
        
        # Handle numeric selector
        try:
            file_num = int(selector)
            if 1 <= file_num <= len(files):
                return files[file_num - 1]['path']
            return None
        except ValueError:
            # If selector is not a number and not "latest", default to first
            return files[0]['path']