# CHANGELOG

All notable changes to SCIONPATHML CLI.

## [1.0]

### Added
- Enhanced error handling for transform commands
- Improved path validation

### Fixed
- Transform-data argument parsing for absolute paths
- Special character handling in file paths

## [0.3]

### Added
#### Data Management Commands
data-overview    # Show all data directories overview
data-show        # Display specific directory details
data-browse      #Browse files interactively (recommended)
data-move        # Move files between directories
data-delete      # Delete data by category
data-search      # Search files by pattern
data-help        # Data management guide
New Options
--interactive #Allow interaction with folders and files
External backup directory support
Changed
Restructured CLI command organization
Enhanced help messages with examples
Improved error messaging
[0.2.3]
Added
Transform Commands
transform           # Simple transform from Data/Archive
transform-data      # Transform with custom path
transform-status    # Show transformation status
transform-help      # Transformation guide
Features
Selective transformations: standard | multipath | all
--output-dir for custom output location
Automatic JSON → CSV conversion
Fixed
Transform-data path parsing
Input path validation
[0.2.2] - BREAKING CHANGES
Added
Log Management System
logs          # List and view log types
view-log      # Navigate specific log files
log-help      # Quick reference guide
Features
--all flag for complete log viewing
File navigation: number or latest
--log-dir for custom log directory
Smart line limits (30/50 default)
Changed
BREAKING: Complete log system restructure
Enhanced UI with color coding
[0.2.1]
Added
Pipeline Command Management
show-cmds           # Display all commands
enable-cmd -m       # Enable specific command
disable-cmd -m      # Disable specific command
enable-category -c  # Enable command category
disable-category -c # Disable command category
enable-all-cmds     # Enable everything
disable-all-cmds    # Disable everything
cmd-help           # Command reference
Features
Command/category name validation
Enhanced error messages with suggestions
[0.2] - BREAKING CHANGES
Added
Core CLI System
# AS Management
add-as -a -i -n     # Add Autonomous System
rm-as -a            # Remove AS
up-as -a -i -n      # Update AS

# Server Management  
add-server -a -i -n # Add bandwidth server
rm-server -a        # Remove server
up-server -a -i -n  # Update server

# Scheduling
-f <minutes>        # Set execution frequency
stop                # Stop automatic execution
show                # Display configuration
Features
Colored CLI output
Cron integration
AS ID and IP validation
Automatic config backup
Changed
BREAKING: New argparse-based architecture
BREAKING: Standardized command format
Removed
BREAKING: Legacy CLI interface
[0.1.2]
Added
Help System
help                  # Quick start
help-examples         # Examples and workflows
help-troubleshooting  #When things break
Features
Interactive welcome messages
Contextual usage examples
[0.1.1]
Added
Modular Architecture
CronManager - Scheduling
ConfigManager - Configuration
HelpManager - Help system
TransformCommands - Data transformation
DataCommands - Data management
LogCommands - Log management
Features
CLI utilities with formatting
Input validation system
[0.1]
Added
Initial SCIONPATHML CLI
Basic SCION network measurement
AS and server configuration
Modular foundation
# Command Categories

## Core Management
show, stop, help
add-as, rm-as, up-as
add-server, rm-server, up-server

## Pipeline Control
show-cmds, enable-cmd, disable-cmd
enable-category, disable-category
enable-all-cmds, disable-all-cmds, cmd-help

## Data Operations
transform, transform-data, transform-status, transform-help
data-overview, data-show, data-move, data-delete, data-search, data-help

## Log Management
logs, view-log, log-help

## Scheduling
-f <minutes>, stop