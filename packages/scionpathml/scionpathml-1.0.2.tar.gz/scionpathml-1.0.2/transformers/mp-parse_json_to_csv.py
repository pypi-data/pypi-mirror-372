#Converts multipath measurement JSON files to CSV format
import os
import json
import pandas as pd
from transformers.parse_json_to_csv import parse_ping, parse_bandwidth  

def collect_multipath_data(base_path):
    all_ping = []
    all_bandwidth = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                fpath = os.path.join(root, file)
                try:
                    with open(fpath) as f:
                        data = json.load(f)

                    src_as = data.get("ia") or data.get("as") or data.get("local_isd_as")

                    if file.startswith("mp-prober"):
                        parsed = parse_ping(data, src_as)
                        all_ping.extend(parsed)

                    elif file.startswith("BW-P_"):
                        parsed = parse_bandwidth(data, src_as)
                        all_bandwidth.extend(parsed)

                except Exception as e:
                    print(f"Error parsing file {fpath}: {e}")

    return all_ping, all_bandwidth

def save_multipath_data(base_path, output_dir="./transformers/datasets"):
    os.makedirs(output_dir, exist_ok=True)
    ping_data, bw_data = collect_multipath_data(base_path)

    if ping_data:
        df_ping = pd.DataFrame(ping_data).sort_values("timestamp")
        df_ping.to_csv(os.path.join(output_dir, "data_PG-MP.csv"), index=False)

    if bw_data:
        df_bw = pd.DataFrame(bw_data).sort_values("timestamp")
        df_bw.to_csv(os.path.join(output_dir, "data_BW-MP.csv"), index=False)


