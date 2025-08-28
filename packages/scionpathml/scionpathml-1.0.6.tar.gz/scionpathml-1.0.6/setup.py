from setuptools import setup, find_packages
import sys
import subprocess

def print_welcome():
    print("\n" + "="*60)
    print("SCIONPATHML CLI Installation Complete!")
    print("="*60)
    print("\n Python package installed successfully")
    
    # Check if scion-apps-bwtester is available
    try:
        result = subprocess.run(['which', 'scion-bwtestclient'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("SCION bandwidth tester found")
        else:
            print("SCION bandwidth tester not found")
            print("   Install with: sudo apt install scion-apps-bwtester")
    except:
        print("Could not check for SCION bandwidth tester")
        print("   Install with: sudo apt install scion-apps-bwtester")
    
    print("\nQuick Start:")
    print("   scionpathml help     # Quick start")
    print("   scionpathml show     # View current configuration")
    
    print("\nSystem Requirements:")
    print("   • SCION infrastructure access")
    print("   • sudo apt install scion-apps-bwtester")
    
    print("\n" + "="*60 + "\n")

def read_requirements():
    """Read requirements from requirements.txt if it exists"""
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

# Base requirements
base_requirements = [
    "pandas>=1.3.0,<3.0.0",        # Data manipulation and CSV handling
    "colorama>=0.4.4",              # Cross-platform colored terminal text
    "tabulate>=0.8.9",              # Pretty-print tabular data
]

# Combine with requirements.txt if exists
additional_requirements = read_requirements()
all_requirements = base_requirements + additional_requirements

print_welcome()

setup(
    name="scionpathml",
    version="1.0.6",
    packages=find_packages(include=["collector*", "runner*", "transformers*", "cli_tools*", "scionpathml*",]), 
    install_requires=all_requirements,  
    entry_points={
        "console_scripts": [
            "scionpathml=scionpathml.cli_tools.scionpathml:main",
        ],
    },
    author="ScionPathML Team",
    author_email="skeshvadi@tru.ca",
    description="Advanced CLI tool for SCION network measurement management and data analysis",
    long_description="""
SCIONPATHML CLI - Advanced SCION Network Measurement Management

A comprehensive command-line interface for managing SCION network measurements,
including AS/Server configuration, pipeline command control, data transformation,
automated scheduling, and log analysis.

Features:
• Complete AS (Autonomous System) and server management
• Pipeline command control with category-based operations  
• Automatic JSON to CSV data transformation
• Advanced log management and viewing
• Data organization and backup operations
• Cron-based scheduling for automated measurements
• Colored CLI output with comprehensive help system

System Requirements:
• SCION network infrastructure access
• SCION bandwidth tester: sudo apt install scion-apps-bwtester
• Python 3.8+ (tested with 3.10.12)


For detailed documentation and examples, run: scionpathml help
    """,
    long_description_content_type="text/plain",
    url="https://github.com/Keshvadi/mpquic-on-scion-ipc/tree/ScionPathML",
    project_urls={
        "Source": "https://github.com/Keshvadi/mpquic-on-scion-ipc",
    },

    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    keywords="scion networking measurement cli data-analysis network-monitoring",
    platforms=["Linux"],
    
    # Optional dependencies for different features
        extras_require={
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.8"],
        "analysis": ["matplotlib>=3.3.0", "seaborn>=0.11.0", "numpy>=1.20.0"],
    },
    
    include_package_data=True,
    package_data={
        "runner": ["*.sh"], 
    },
    zip_safe=False,
)

# Additional post-install checks
def post_install_check():
    """Check system requirements after installation"""
    print("\nPost-Installation System Check:")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} - Compatible")
    else:
        print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires 3.8+")
    
    # Check pandas installation
    try:
        import pandas as pd
        print(f"Pandas {pd.__version__} - Installed")
    except ImportError:
        print("Pandas - Not found (required for data transformation)")
    
    # Check for SCION tools
    scion_tools = ['scion-bwtestclient', 'scion-bwtestserver', 'scion']
    for tool in scion_tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{tool} - Found")
            else:
                print(f" {tool} - Not found")
        except:
            print(f"{tool} - Could not check")
    
if __name__ == "__main__":
    post_install_check()