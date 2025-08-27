# ScionPathML

A Python toolkit for SCION network measurement and machine learning dataset generation.

## Overview

ScionPathML provides a command-line interface for systematic SCION network measurement campaigns and data processing. The toolkit coordinates SCION's native measurement tools (`scion ping`, `scion-bwtestclient`, `scion traceroute`, `scion showpaths`) through automated scheduling and converts raw measurement outputs to analysis-ready CSV datasets.

## Installation

```bash
git clone https://github.com/Keshvadi/mpquic-on-scion-ipc.git
cd installation-folder/mpquic-on-scion-ipc
pip install -e .
```
## Prerequisites
- Python 3.8+ 
- SCION infrastructure access (SCIONLab and active AS)
- SCION measurement tools for bandwidth: `sudo apt install scion-apps-bwtester`



## Network Configuration 

### Configure autonomous systems and server
```bash
#AS
scionpathml add-as -a 19-ffaa:1:11de -i 192.168.1.100 -n MyAS          #Add your AS
scionpathml up-as -a 19-ffaa:1:11de -i 192.168.1.101 -n UpdatedAS      #Update AS details
scionpathml rm-as -a 19-ffaa:1:11de                                    #Remove AS

#Server
scionpathml add-server -a 19-ffaa:1:22ef -i 10.0.0.50 -n MyServer      #Add your server
scionpathml up-server -a 19-ffaa:1:22ef -i 10.0.0.51 -n UpdatedServer  #Update server details
scionpathml rm-server -a 19-ffaa:1:22ef                                #Remove server
```
### View configuration
```bash
scionpathml show    #See your current configuration
```
## Measurement Control

### Control measurement pipeline
```bash
scionpathml show-cmds                     #Display all commands and their status
scionpathml enable-cmd -m bandwidth       #Enable bandwidth command
scionpathml disable-cmd -m bandwidth      #Disable bandwidth command
scionpathml enable-category -c tracing    #Enable all commands in category tracing
scionpathml disable-category -c tracing   #Disable all commands in category tracing
```
### Schedule automated measurements & One time run
```bash
scionpathml -f 30  # Run every 30 minutes
scionpathml run    # Test run the pipeline right now

```
## Data Processing

### Transform JSON measurements to CSV
```bash
scionpathml transform                                 #Convert JSON files to CSV
scionpathml transform-data /path/to/measurements      #Transform from custom path
scionpathml transform multipath --output-dir /output/ #Custom output with default data
```
## Manage datasets
```bash
scionpathml data-overview                       #Check current data status
scionpathml data-show Archive                   #Show detailed Archive contents
scionpathml data-show Archive --interractive    #Browse Archive interactively
scionpathml data-move History Archive           #Move History to Archive
```
## View logs and status
```bash
scionpathml logs pipeline                 #Last 30 lines of pipeline.log
scionpathml view-log bandwidth latest     #View latest file (highest number)
scionpathml view-log bandwidth            #View file 1 (last 50 lines)

```
## Measurement Types

Path Discovery: scion showpaths coordination  
Latency Testing: scion ping with configurable parameters  
Bandwidth Testing: scion-bwtestclient throughput measurement  
Path Analysis: scion traceroute hop-by-hop latency  
Multipath Testing: mp-prober and mp-bandwidth for concurrent measurements  
Path Comparison: Historical path availability tracking  


## Data Organization

Data/  
├── Archive/     # Archive measurement data  
├── Currently/   # Current measurement data  
├── History/     # Preivous measurement data  
└── Logs/        # Execution and error logs  


## License
MIT License


## CSV to DataFrame Guide

If necessary, you can also convert your CSV file to a DataFrame. Here is some documentation to help you do this:

### Installation of pandas

Ensure you have Python and the pandas library installed. You can install pandas via pip if necessary:

```bash
pip install pandas
```
### Example Code

```python
import pandas as pd

# Load data from CSV into a DataFrame
df = pd.read_csv('your_file.csv')
print(df.head())
```


