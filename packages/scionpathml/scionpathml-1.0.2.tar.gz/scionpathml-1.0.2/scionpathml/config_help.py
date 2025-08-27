#Help system for AS and server management commands
from cli_utils import *

class ConfigHelpManager:
    @staticmethod
    def show_config_help():
        """Show comprehensive AS and server management help"""
        print_header("SCIONPATHML - AS & SERVER MANAGEMENT")
        
        print_section("WHAT ARE AS AND SERVERS?")
        print("• AS (Autonomous Systems) - SCION network nodes you want to monitor and get data from him")
        print("• Servers - Endpoints for bandwidth testing (optional but recommended)")
        
        print_section("AS MANAGEMENT")
        
        print(f"{Colors.BOLD}Adding an AS:{Colors.END}")
        print_example("scionpathml add-as -a 19-ffaa:1:11de -i 192.168.1.100 -n MyAS", 
                     "Add new AS ")
        
        print(f"\n{Colors.BOLD}Updating an AS:{Colors.END}")
        print_example("scionpathml up-as -a 19-ffaa:1:11de -i 192.168.1.101 -n UpdatedAS", 
                     "Update AS details")
        
        print(f"\n{Colors.BOLD}Removing an AS:{Colors.END}")
        print_example("scionpathml rm-as -a 19-ffaa:1:11de", "Remove AS ")
        
        print_section("SERVER MANAGEMENT")
        
        print(f"{Colors.BOLD}Adding a Server:{Colors.END}")
        print_example("scionpathml add-server -a 19-ffaa:1:22ef -i 10.0.0.50 -n MyServer", 
                     "Add new server")
        
        print(f"\n{Colors.BOLD}Updating a Server:{Colors.END}")
        print_example("scionpathml up-server -a 19-ffaa:1:22ef -i 10.0.0.51 -n UpdatedServer", 
                     "Update server details")
        
        print(f"\n{Colors.BOLD}Removing a Server:{Colors.END}")
        print_example("scionpathml rm-server -a 19-ffaa:1:22ef", "Remove server")
        
        print_section("PARAMETER REQUIREMENTS")
        
        print(f"{Colors.BOLD}AS ID Format (-a):{Colors.END}")
        print("• Pattern: number-ffaa:hex:hex")
        print("• Examples: 19-ffaa:1:11de, 64-ffaa:0:110, 17-ffaa:0:1101")
        
        print(f"\n{Colors.BOLD}IP Address (-i):{Colors.END}")
        print("• Must be valid IPv4 address")
        print("• Examples: 192.168.1.100, 10.0.0.50, 172.16.1.10")
        
        print(f"\n{Colors.BOLD}Name (-n):{Colors.END}")
        print("• Alphanumeric characters, hyphens, and underscores only")
        print("• Max 50 characters")
        print("• Examples: ProductionAS, test-server-1, BW_Server_Main")

        