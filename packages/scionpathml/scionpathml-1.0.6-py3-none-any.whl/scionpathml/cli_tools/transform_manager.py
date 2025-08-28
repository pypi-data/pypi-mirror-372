#Core transformation logic and file processing
from pathlib import Path
from .cli_utils import print_error, print_success, print_info, print_example, print_header, print_section, Colors
from scionpathml.cli_tools.path_utils import transformers_dir

class TransformManager:
    """Manage JSON to CSV data transformation"""
    
    def __init__(self):
        self.transformers_dir = transformers_dir()
        self.default_output_dir = str(self.transformers_dir / "datasets")
    
    def check_scripts_exist(self):
        """Check if transformation scripts exist"""
        standard_script = self.transformers_dir / "parse_json_to_csv.py"
        multipath_script = self.transformers_dir / "mp-parse_json_to_csv.py"
        print(multipath_script)
        
        missing = []
        if not standard_script.exists():
            missing.append("parse_json_to_csv.py")
        if not multipath_script.exists():
            missing.append("mp-parse_json_to_csv.py")
        
        return missing
    
    def validate_data_path(self, data_path):
        """Validate data path exists and contains JSON files"""
        if not data_path:
            return False, "No data path provided"
        
        path = Path(data_path)
        if not path.exists():
            return False, f"Data path does not exist: {data_path}"
        
        if not path.is_dir():
            return False, f"Data path is not a directory: {data_path}"
        
        # Check for JSON files
        json_files = list(path.rglob("*.json"))
        if not json_files:
            return False, f"No JSON files found in: {data_path}"
        
        return True, f"Found {len(json_files)} JSON files"
    
    def prepare_output_dir(self, output_dir):
        """Create output directory if it doesn't exist"""
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            return True, f"Output directory ready: {output_dir}"
        except Exception as e:
            return False, f"Cannot create output directory: {e}"
    
    def run_standard_transform(self, data_path, output_dir=None):
        """Run standard JSON to CSV transformation"""
        output_dir = output_dir or self.default_output_dir
        
        print_header("STANDARD DATA TRANSFORMATION")
        print_info(f"Data source: {data_path}")
        print_info(f"Output directory: {output_dir}")
        print()
        
        # Check if script exists
        missing_scripts = self.check_scripts_exist()
        if "parse_json_to_csv.py" in missing_scripts:
            print_error("parse_json_to_csv.py not found in transformers/ directory")
            return False
        
        # Validate inputs
        valid, message = self.validate_data_path(data_path)
        if not valid:
            print_error(message)
            return False
        print_success(message)
        
        valid, message = self.prepare_output_dir(output_dir)
        if not valid:
            print_error(message)
            return False
        print_success(message)
        
        
        try:
            # Run the transformation script
            script_path = self.transformers_dir / "parse_json_to_csv.py"
            
            # Modify the script execution to use custom paths
            import importlib.util
            spec = importlib.util.spec_from_file_location("parse_json_to_csv", script_path)
            transform_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(transform_module)
            
            # Call the transformation function with custom paths
            transform_module.save_dfs(data_path, output_dir)
            
            print()
            print_success("Standard transformation completed!")
            self._show_generated_files(output_dir, pattern="data_*.csv", exclude_pattern="*-MP.csv")
            
            return True
            
        except Exception as e:
            print_error(f"Standard transformation failed: {e}")
            return False

    def run_multipath_transform(self, data_path, output_dir=None):
        """Run multipath JSON to CSV transformation"""
        output_dir = output_dir or self.default_output_dir
        
        print_header("MULTIPATH DATA TRANSFORMATION")
        print_info(f"Data source: {data_path}")
        print_info(f"Output directory: {output_dir}")
        print()
        
        # Check if script exists
        missing_scripts = self.check_scripts_exist()
        if "mp-parse_json_to_csv.py" in missing_scripts:
            print_error("mp-parse_json_to_csv.py not found in transformers/ directory")
            return False
        
        # Validate inputs
        valid, message = self.validate_data_path(data_path)
        if not valid:
            print_error(message)
            return False
        print_success(message)
        
        valid, message = self.prepare_output_dir(output_dir)
        if not valid:
            print_error(message)
            return False
        print_success(message)

        
        try:
            # Run the multipath transformation script
            script_path = self.transformers_dir / "mp-parse_json_to_csv.py"
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("mp_parse_json_to_csv", script_path)
            transform_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(transform_module)
            
            # Call the transformation function with custom paths
            transform_module.save_multipath_data(data_path, output_dir)
            
            print()
            print_success("Multipath transformation completed!")
            self._show_generated_files(output_dir, pattern="data_*-MP.csv")
            
            return True
            
        except Exception as e:
            print_error(f"Multipath transformation failed: {e}")
            return False
    
    def run_all_transforms(self, data_path, output_dir=None):
        """Run both standard and multipath transformations"""
        print_header("COMPLETE DATA TRANSFORMATION")
        print_info("Running both standard and multipath transformations...")
        print()
        
        success_standard = self.run_standard_transform(data_path, output_dir)
        print()
        success_multipath = self.run_multipath_transform(data_path, output_dir)
        
        print()
        print_header("TRANSFORMATION SUMMARY")
        
        if success_standard and success_multipath:
            print_success("All transformations completed successfully!")
        elif success_standard:
            print_success("Standard transformation completed")
            print_error("Multipath transformation failed")
        elif success_multipath:
            print_error("Standard transformation failed")
            print_success("Multipath transformation completed")
        else:
            print_error("All transformations failed")
            return False
        
        # Show summary of all files
        output_dir = output_dir or self.default_output_dir
        self._show_transformation_summary(output_dir)
        
        return success_standard or success_multipath
    
    def show_transform_status(self, output_dir=None):
        """Show current transformation status"""
        output_dir = output_dir or self.default_output_dir
        output_path = Path(output_dir)
        
        print_header("TRANSFORMATION STATUS")
        print_info(f"Output directory: {output_path.absolute()}")
        
        if not output_path.exists():
            print_error("Output directory does not exist")
            print_info("Run transformation first:")
            print_example("scionpathml transform-data /path/to/json/files", "Transform data")
            return
        
        # Show CSV files
        csv_files = list(output_path.glob("data_*.csv"))
        if not csv_files:
            print_error("No CSV files found")
            print_info("Run transformation first:")
            print_example("scionpathml transform-data /path/to/json/files", "Transform data")
            return
        
        print_success(f"Found {len(csv_files)} CSV files:")
        print()
        
        # Separate standard and multipath files
        standard_files = [f for f in csv_files if not f.name.endswith("-MP.csv")]
        multipath_files = [f for f in csv_files if f.name.endswith("-MP.csv")]
        
        if standard_files:
            print_section("Standard Files")
            for csv_file in sorted(standard_files):
                self._show_file_info(csv_file)
        
        if multipath_files:
            print_section("Multipath Files")
            for csv_file in sorted(multipath_files):
                self._show_file_info(csv_file)
        
        # Show total size
        total_size = sum(f.stat().st_size for f in csv_files) / 1024  # KB
        print()
        print_info(f"Total size: {total_size:.1f} KB")
    
    def _show_generated_files(self, output_dir, pattern, exclude_pattern=None):
        """Show generated files matching pattern"""
        output_path = Path(output_dir)
        files = list(output_path.glob(pattern))
        
        if exclude_pattern:
            exclude_files = set(output_path.glob(exclude_pattern))
            files = [f for f in files if f not in exclude_files]
        
        if files:
            print_info("Generated files:")
            for csv_file in sorted(files):
                self._show_file_info(csv_file, indent="   ")
    
    def _show_file_info(self, file_path, indent=""):
        """Show file information"""
        file_size = file_path.stat().st_size / 1024  # KB
        from datetime import datetime
        modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        mod_time = modified.strftime('%Y-%m-%d %H:%M')
        print(f"{indent} {file_path.name:<20} ({file_size:>6.1f} KB) - {mod_time}")
    
    def _show_transformation_summary(self, output_dir):
        """Show complete transformation summary"""
        output_path = Path(output_dir)
        all_files = list(output_path.glob("data_*.csv"))
        
        if all_files:
            total_size = sum(f.stat().st_size for f in all_files) / 1024  # KB
            print()
            print_info(f"Total files: {len(all_files)}")
            print_info(f"Total size: {total_size:.1f} KB")
            print_info(f"Location: {output_path.absolute()}")