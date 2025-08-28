#Manages scheduled execution and cron job operations
import os
import subprocess
from .cli_utils import *

class CronManager:
    def __init__(self, script_name="pipeline.sh", env_var="SCRIPT_PATH"):
        self.script_name = script_name
        self.env_var = env_var


    def read_crontab(self):
        """Read current user's crontab"""
        result = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout if result.returncode == 0 else ""

    def write_crontab(self, content):
        """Write content to user's crontab"""
        subprocess.run(["crontab", "-"], input=content, text=True)
    

    def get_current_cron_frequency(self):
        """Get the current cron frequency for scionpathml."""
        current_cron = self.read_crontab()
        for line in current_cron.splitlines():
            if "pipeline.sh" in line and line.strip() and not line.strip().startswith("#"):
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0].startswith("*/"):
                    try:
                        return int(parts[0][2:])
                    except ValueError:
                        return None
        return None
    
    def get_dynamic_script_path(self):
        """Dynamically find the pipeline.sh script relative to the installed package"""
        try:
            # Get the current file's location
            current_file = os.path.abspath(__file__)
            
            # Navigate to the package root
            cli_tools_dir = os.path.dirname(current_file)        
            scionpathml_dir = os.path.dirname(cli_tools_dir)     
            package_root = os.path.dirname(scionpathml_dir)      
            
            # Build path to pipeline.sh
            script_path = os.path.join(package_root, "runner", self.script_name)
            
            if os.path.isfile(script_path):
                return script_path
            else:
                # Try alternative: maybe runner is inside scionpathml
                alt_script_path = os.path.join(scionpathml_dir, "runner", self.script_name)
                if os.path.isfile(alt_script_path):
                    return alt_script_path
                    
                raise FileNotFoundError(f"Could not find {self.script_name} at expected locations")
                
        except Exception as e:
            raise EnvironmentError(f"Failed to locate script dynamically: {e}")

    def get_script_path(self, path_override=None):
        """Get the path to pipeline.sh script with multiple fallback methods."""
        
        # Method 1: Manual override (highest priority)
        if path_override:
            script_path = os.path.join(path_override, self.script_name)
            print_info(f"Using manual path override: {script_path}")
            return script_path
            
        # Method 2: Environment variable
        env_path = os.getenv(self.env_var)
        if env_path:
            script_path = os.path.join(env_path, self.script_name)
            print_info(f"Using environment variable path: {script_path}")
            return script_path
            
        # Method 3: Dynamic detection based on package location (NEW!)
        try:
            script_path = self.get_dynamic_script_path()
            print_info(f"Using dynamic package path: {script_path}")
            return script_path
        except Exception as e:
            print_warning(f"Dynamic detection failed: {e}")
            
        # Method 4: Legacy automatic detection (fallback)
        try:
            current_path = os.path.abspath(__file__)
            parts = current_path.split(os.sep)
            if "mpquic-on-scion-ipc" in parts:
                mpquic_index = parts.index("mpquic-on-scion-ipc")
                base_path = os.sep.join(parts[:mpquic_index + 1])
                script_path = os.path.join(base_path, "runner", self.script_name)
                if os.path.isfile(script_path):
                    print_info(f"Using legacy detection: {script_path}")
                    return script_path
        except Exception:
            pass
            
        # Method 5: Try some common locations
        common_locations = [
            os.path.join(os.path.expanduser("~"), ".local", "lib", "python*", "site-packages", "runner", self.script_name),
            os.path.join("/usr", "local", "lib", "python*", "site-packages", "runner", self.script_name),
        ]
        
        for location_pattern in common_locations:
            import glob
            matches = glob.glob(location_pattern)
            if matches and os.path.isfile(matches[0]):
                print_info(f"Found at common location: {matches[0]}")
                return matches[0]
                
        # If all methods fail
        raise EnvironmentError(
            f"Could not locate {self.script_name} automatically.\n"
            f"{Colors.CYAN}Solutions:{Colors.END}\n"
            f"   1. Use -p flag: scionpathml -f 30 -p /path/to/runner\n"
            f"   2. Set environment: export {self.env_var}=/path/to/runner\n"
            f"   3. Ensure package is properly installed: pip install -e ."
        )
    

    def explain_frequency_calculation(self):
        """Explain how frequency calculation works"""
        print_info("How frequency calculation works:")
        print("  • Each AS needs time to complete its measurements")
        print("  • We recommend 10 minutes per AS to avoid conflicts")
        print("  • Formula: Number of AS × 10 = Recommended frequency")
        print()
        print("Examples:")
        print("    2 AS → 20 minutes frequency")
        print("    4 AS → 40 minutes frequency") 
        print("    6 AS → 60 minutes frequency")

    def check_frequency_warning(self, config):
        """Check if current frequency needs adjustment and show warnings"""
        unique_ases = set(config.AS_FOLDER_MAP.keys()) | set(config.AS_TARGETS.keys())
        num_ases = len(unique_ases)
        recommended = num_ases * 10
        current = self.get_current_cron_frequency()
        
        if current is None:
            print_warning("No cron frequency currently set for scionpathml")
            self.explain_frequency_calculation()
            print_example(f"scionpathml -f {recommended}", "Set optimal frequency for your configuration")
            return
        
        if current < recommended:
            print_warning(f"Current frequency ({current} min) might be too aggressive!")
            print(f"  • You have {num_ases} AS(es) configured")
            print(f"  • Current frequency: {current} minutes")
            print(f"  • Recommended frequency: {recommended} minutes")
            print()
            print_info("Why this matters:")
            print("  • Too frequent execution can cause resource conflicts")
            print("  • Each AS measurement needs time to complete properly")
            print("  • Overlapping executions can produce results without data")
            print()
            print_example(f"scionpathml -f {recommended}", "Update to recommended frequency")

    def _check_script_format(self, script_path):
        """Check if script has proper format and try to fix common issues"""
        try:
            with open(script_path, 'rb') as f:
                first_bytes = f.read(50)
            
            # Check for shebang
            if not first_bytes.startswith(b'#!'):
                print_warning("Script missing shebang line")
                print_info("Attempting to fix...")
                try:
                    with open(script_path, 'r') as f:
                        content = f.read()
                    with open(script_path, 'w') as f:
                        f.write('#!/bin/bash\n' + content)
                    print_success("Added #!/bin/bash shebang")
                except Exception as e:
                    print_error(f"Could not add shebang: {e}")
                    return False
            
            # Check for Windows line endings
            if b'\r\n' in first_bytes:
                print_warning("Script has Windows line endings")
                print_info("Attempting to convert...")
                try:
                    subprocess.run(['dos2unix', script_path], check=True, capture_output=True)
                    print_success("Converted line endings to Unix format")
                except subprocess.CalledProcessError:
                    print_error("dos2unix command failed - you may need to install it")
                    return False
                except FileNotFoundError:
                    print_error("dos2unix not found - trying manual conversion")
                    try:
                        with open(script_path, 'rb') as f:
                            content = f.read()
                        content = content.replace(b'\r\n', b'\n')
                        with open(script_path, 'wb') as f:
                            f.write(content)
                        print_success("Manually converted line endings")
                    except Exception as e:
                        print_error(f"Manual conversion failed: {e}")
                        return False
            
            return True
            
        except Exception as e:
            print_error(f"Could not check script format: {e}")
            return False

    def run_once(self):
        """Execute the pipeline script once immediately"""
        print_header("RUN PIPELINE ONCE")
        
        try:
            full_path = self.get_script_path()
        except EnvironmentError as e:
            print_error(str(e))
            return False
            
        if not os.path.isfile(full_path):
            print_error(f"Script not found at: {full_path}")
            print_info("Check that the file exists and path is correct")
            return False
        
        if not os.access(full_path, os.X_OK):
            print_info("Script is not executable, fixing permissions...")
            try:
                os.chmod(full_path, 0o755)
                print_success("Made script executable")
            except Exception as e:
                print_error(f"Could not make script executable: {e}")
                print_info(f"Try: chmod +x {full_path}")
                return False
        print()
        
        response = input("Execute pipeline script now? (y/N): ")
        if response.lower() != 'y':
            print_info("Execution cancelled")
            return False
        
        print_success("Starting pipeline execution...")
        print("=" * 60)
        
        # Change to script directory for proper execution context
        script_dir = os.path.dirname(full_path)
        original_dir = os.getcwd()
        
        try:
            os.chdir(script_dir)      
            # Execute the script
            start_time = subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
            print_info(f"Started at: {start_time}")
            print()
            
            # Run with real-time output
            process = subprocess.Popen(
                [full_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            return_code = process.returncode
            
            print()
            print("=" * 60)
            end_time = subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
            print_info(f"Finished at: {end_time}")
            
            if return_code == 0:
                print_success("Pipeline executed successfully!")
                print()
                print_info("Next steps:")
                print_example("scionpathml data-overview", "Check your measurement data")
                print_example("scionpathml data-browse", "Browse data interactively")
                print_example("scionpathml logs pipeline", "View pipeline logs")
                return True
            else:
                print_error(f"Pipeline failed with exit code: {return_code}")
                print()
                print_info("Troubleshooting:")
                print_example("scionpathml logs pipeline --all", "Check pipeline logs for errors")
                print_example("scionpathml show-cmds", "Verify enabled commands")
                return False
                
        except OSError as e:
            if e.errno == 8:  # Exec format error
                print_error("Script format error detected")
                print_info("Attempting to fix common script issues...")
                
                if self._check_script_format(full_path):
                    print_info("Script format issues fixed, trying again...")
                    # Try one more time after fixes
                    try:
                        process = subprocess.Popen([full_path], stdout=subprocess.PIPE, 
                                                 stderr=subprocess.STDOUT, universal_newlines=True)
                        for line in process.stdout:
                            print(line.rstrip())
                        process.wait()
                        if process.returncode == 0:
                            print_success("Pipeline executed successfully after fixes!")
                            return True
                        else:
                            print_error(f"Still failed with exit code: {process.returncode}")
                    except Exception as retry_error:
                        print_error(f"Still failed: {retry_error}")
                else:
                    print_error("Could not fix script format issues")
                    print()
                    print_info("Manual fixes needed:")
                    print(f"1. Check first line: should be '#!/bin/bash'")
                    print(f"2. Convert line endings: dos2unix {full_path}")
                    print(f"3. Verify file format: file {full_path}")
                    
                return False
            else:
                print_error(f"Error executing pipeline: {e}")
                return False
                
        except KeyboardInterrupt:
            print_warning("\nPipeline execution interrupted by user")
            if process.poll() is None:
                process.terminate()
                process.wait()
            return False
        except Exception as e:
            print_error(f"Error executing pipeline: {e}")
            return False
        finally:
            # Always return to original directory
            os.chdir(original_dir)

    def update_cron(self, frequency, path_override=None, config=None):
        """Update cron job with new frequency."""
        print_header(f"UPDATING CRON FREQUENCY TO {frequency} MINUTES")
        
        try:
            full_path = self.get_script_path(path_override)
        except EnvironmentError as e:
            print_error(str(e))
            return False
            
        if not os.path.isfile(full_path):
            print_error(f"Script not found at: {full_path}")
            print_info("Please check the path and try again")
            return False
        
        cron_line = f"*/{frequency} * * * * {full_path}"
        current_cron = self.read_crontab()
        
        # Remove existing entries to avoid duplicates
        existing_lines = [line for line in current_cron.splitlines() if "pipeline.sh" not in line]
        
        # Add new cron line
        existing_lines.append(cron_line)
        new_cron_content = "\n".join(existing_lines) + "\n"
        
        self.write_crontab(new_cron_content)
        
        print_success(f"Cron job updated successfully!")
        print(f"  • Frequency: Every {frequency} minutes")
        
        # Check if frequency is optimal
        if config:
            unique_ases = set(config.AS_FOLDER_MAP.keys()) | set(config.AS_TARGETS.keys())
            num_ases = len(unique_ases)
            recommended = num_ases * 10
            
            if frequency == recommended:
                print_success("Perfect! This frequency matches our recommendation.")
            elif frequency < recommended:
                print_warning(f"Consider using {recommended} minutes for {num_ases} AS(es)")
                self.explain_frequency_calculation()
            else:
                print_info(f"This is more conservative than our {recommended}-minute recommendation")
                print("  • More conservative frequencies are generally safer")
                print("  • You can always decrease it later if needed")
        
        return True

    def stop_cron(self):
        """Remove scionpathml cron job"""
        print_header("STOPPING SCIONPATHML CRON JOB")
        
        current_cron = self.read_crontab()
        original_lines = current_cron.splitlines()
        remaining_lines = [line for line in original_lines if "pipeline.sh" not in line]
        
        removed_count = len(original_lines) - len(remaining_lines)
        
        if removed_count == 0:
            print_info("No active scionpathml cron jobs found")
            print("  • The cron job might already be stopped")
            print("  • Or it was never configured")
            print()
            print_example("scionpathml -f 30", "Start with 30-minute frequency")
            return
        
        self.write_crontab("\n".join(remaining_lines) + "\n" if remaining_lines else "")
        
        print_success(f"Removed {removed_count} cron job(s)")
        print("  • scionpathml is no longer scheduled to run automatically")
        print("  • You can still run it manually anytime")
        print()
        print_example("scionpathml -f 30", "Restart with 30-minute frequency")
        print_example("scionpathml run", "Execute pipeline once")