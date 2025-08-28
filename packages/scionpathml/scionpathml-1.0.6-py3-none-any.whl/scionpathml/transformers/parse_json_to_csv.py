#Converts standard measurement JSON files to CSV format
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

def extract_timestamp_from_filename(filename):
    try:
        for part in filename.split("_"):
            if len(part) >= 16 and "T" in part:
                return datetime.fromisoformat(part)
    except Exception:
        pass
    return datetime.now()

def format_sequence_with_ifaces(sequence_str):
    parts = sequence_str.split()
    formatted_parts = []
    for part in parts:
        if "#" in part:
            as_part, ifaces = part.split("#", 1)
            formatted_parts.append(f"{as_part} [in,out]=({ifaces})")
        else:
            formatted_parts.append(part)
    return " ".join(formatted_parts)

def parse_ping(data, src_as):
    rows = []
    timestamp = data.get("timestamp") or datetime.now().isoformat()
    dst_as = data.get("ia")
    
    # Check if there's an error or no probes
    if data.get("error") or not data.get("probes"):
        # Create failure entry
        row = {
            "timestamp": timestamp,
            "src_as": src_as,
            "dst_as": dst_as,
            "path_fingerprint": None,
            "sequence": None,
            "sent (count)": 0,
            "received (count)": 0,
            "loss_rate (%)": 100.0, 
            "min_rtt (ms)": np.nan,
            "avg_rtt (ms)": np.nan,
            "max_rtt (ms)": np.nan,
            "mdev_rtt (ms)": np.nan,
            "replies_rtt (ms)": [],
            "available": 0,
            "failure_reason": data.get("error", "no_probes_found"),
            "data_quality": "failed"
        }
        rows.append(row)
        return rows

    # Process successful probes
    for probe in data.get("probes", []):
        rtts = [r["round_trip_time"] for r in probe.get("ping_result", {}).get("replies", []) if r.get("state") == "success"]
        stats = probe.get("ping_result", {}).get("statistics", {})
        replies = probe.get("ping_result", {}).get("replies", [])
        sent = stats.get("sent", 0)
        received = stats.get("received", 0)
        loss_rate = (1 - received / sent) * 100 if sent > 0 else 100.0
        path_info = probe.get("ping_result", {}).get("path", {})
        sequence = path_info.get("sequence")
        hops = path_info.get("hops", [])
        fingerprint = probe.get("fingerprint")
        src_sequence = sequence.split()[0].split("#")[0] if sequence else None

        if sequence:
            sequence = format_sequence_with_ifaces(sequence)

        # Determine data quality
        data_quality = "good"
        if loss_rate and loss_rate > 10:  
            data_quality = "degraded"
        elif sent == 0 or received == 0:
            data_quality = "failed"

        row = {
            "timestamp": timestamp,
            "src_as": src_sequence,
            "dst_as": dst_as,
            "path_fingerprint": fingerprint,
            "sequence": sequence,
            "sent (count)": sent,
            "received (count)": received,
            "loss_rate (%)": loss_rate,
            "min_rtt (ms)": stats.get("min_rtt"),
            "avg_rtt (ms)": stats.get("avg_rtt"),
            "max_rtt (ms)": stats.get("max_rtt"),
            "mdev_rtt (ms)": stats.get("mdev_rtt"),
            "replies_rtt (ms)": rtts,
            "available": 1 if data_quality != "failed" else 0,
            "failure_reason": None if data_quality != "failed" else "measurement_failed",
            "data_quality": data_quality
        }

        rows.append(row)

    return rows

def parse_bandwidth(data, src_as):
    rows = []
    timestamp = data.get("timestamp") or datetime.now().isoformat()

    def parse_bps(value):
        try:
            if value is None or value == "" or value == 0:
                return 0.0
            
            # Convert to string first in case it's not already a string
            value_str = str(value).strip()
            
            # Handle empty string
            if not value_str:
                return 0.0
            
            # Handle the case where value might just be a number
            if "/" not in value_str:
                return float(value_str)
            
            # Original logic for "X/Y" format
            parts = value_str.split("/")
            if len(parts) >= 2:
                # Take the last part and extract the first number
                last_part = parts[-1].strip()
                # Split by space and take first element (the number)
                number_part = last_part.split()[0] if last_part.split() else "0"
                return float(number_part)
            else:
                return float(parts[0])
                
        except (ValueError, IndexError, AttributeError) as e:
            print(f"Warning: Could not parse BPS value '{value}': {e}")
            return 0.0

    def safe_loss_rate(loss_value):
        """Safely convert loss rate to float percentage"""
        try:
            if loss_value is None:
                return 0.0
            if isinstance(loss_value, str):
                # Remove any % symbol and convert
                clean_value = loss_value.replace('%', '').strip()
                return float(clean_value)
            return float(loss_value)
        except (ValueError, AttributeError):
            return 0.0

    # Check for errors 
    has_error = (
        data.get("error") or 
        data.get("error_type") or  
        ((data.get("target") or data.get("target_server")) and not data.get("paths") and not data.get("result"))
    )
    
    if has_error:
        # Get destination from target_server if available
        dst_as = None
        if data.get("target_server"):
            dst_as = data.get("target_server", {}).get("ia")
        elif data.get("ia"):
            dst_as = data.get("ia")
        
        # Get target info from either target or direct fields
        target_info = data.get("target", {})
        if not target_info:
            # Extract from direct fields (your data structure)
            target_info = {
                "tier_mbps": data.get("tier_mbps"),
                "duration_sec": data.get("duration_sec"),
                "packet_size_bytes": data.get("packet_size_bytes"),
                "packet_count": data.get("packet_count")
            }
        
        row = {
            "timestamp": timestamp,
            "src_as": src_as,
            "dst_as": dst_as,
            "path_fingerprint": data.get("fingerprint"),
            "target_mbps (Mbps)": target_info.get("tier_mbps"),
            "target_duration_sec (sec)": target_info.get("duration_sec"),
            "target_packet_size_bytes (bytes)": target_info.get("packet_size_bytes"),
            "target_packet_count (count)": target_info.get("packet_count"),
            "sequence": data.get("sequence"),
            "sc_attempted_bps (bps)": 0,
            "sc_achieved_bps (bps)": 0,
            "sc_loss_rate_percent (%)": 100.0,
            "sc_interarrival (ms)": None,
            "cs_attempted_bps (bps)": 0,
            "cs_achieved_bps (bps)": 0,
            "cs_loss_rate_percent (%)": 100.0,
            "cs_interarrival (ms)": None,
            "avg_bandwidth (Mbps)": 0.0,
            "available": 0,  
            "failure_reason": data.get("error") or data.get("error_type") or "no_measurement_data",
            "data_quality": "failed"
        }
        rows.append(row)
        return rows

    # Process successful measurements
    if "paths" in data:
        for path in data.get("paths", []):
            try:
                f = path.get("fingerprint")
                sequence_str = path.get("sequence", "")
                sequence_parts = [p.strip() for p in sequence_str.split("->") if p.strip()]
                src_as_path = sequence_parts[0] if sequence_parts else src_as
                dst_as_path = sequence_parts[-1] if sequence_parts else None

                res = path.get("result", {})
                
                
                sc = res.get("S->C results", {})
                cs = res.get("C->S results", {})
                
                if not sc and not cs:
                  
                    target = path.get("target", {})
                    row = {
                        "timestamp": timestamp,
                        "src_as": src_as_path,
                        "dst_as": dst_as_path,
                        "path_fingerprint": f,
                        "target_mbps (Mbps)": target.get("tier_mbps"),
                        "target_duration_sec (sec)": target.get("duration_sec"),
                        "target_packet_size_bytes (bytes)": target.get("packet_size_bytes"),
                        "target_packet_count (count)": target.get("packet_count"),
                        "sequence": sequence_str,
                        "sc_attempted_bps (bps)": 0,
                        "sc_achieved_bps (bps)": 0,
                        "sc_loss_rate_percent (%)": 100.0,
                        "sc_interarrival (ms)": None,
                        "cs_attempted_bps (bps)": 0,
                        "cs_achieved_bps (bps)": 0,
                        "cs_loss_rate_percent (%)": 100.0,
                        "cs_interarrival (ms)": None,
                        "avg_bandwidth (Mbps)": 0.0,
                        "available": 0,
                        "failure_reason": "no_measurement_results",
                        "data_quality": "failed"
                    }
                    rows.append(row)
                    continue

                target = path.get("target", {})

                # Safely parse loss rates
                sc_loss = safe_loss_rate(sc.get("loss_rate"))
                cs_loss = safe_loss_rate(cs.get("loss_rate"))
                avg_loss = (sc_loss + cs_loss) / 2

                # Parse bandwidth values safely
                bw_sc = parse_bps(sc.get("achieved_bps", "0"))
                bw_cs = parse_bps(cs.get("achieved_bps", "0"))
                
               
                if bw_sc == 0 and bw_cs == 0:
                    data_quality = "failed"
                    available = 0
                    failure_reason = "zero_bandwidth_measured"
                    avg_bandwidth = 0.0
                else:
                    # Calculate average bandwidth safely
                    if bw_sc > 0 and bw_cs > 0:
                        avg_bandwidth = (bw_sc + bw_cs) / 2
                    elif bw_sc > 0:
                        avg_bandwidth = bw_sc
                    elif bw_cs > 0:
                        avg_bandwidth = bw_cs
                    else:
                        avg_bandwidth = 0.0
                    
                    # Determine data quality
                    if avg_loss > 5:  # >5% loss
                        data_quality = "degraded"
                    else:
                        data_quality = "good"
                    
                    available = 1
                    failure_reason = None

                row = {
                    "timestamp": timestamp,
                    "src_as": src_as_path,
                    "dst_as": dst_as_path,
                    "path_fingerprint": f,
                    "target_mbps (Mbps)": target.get("tier_mbps"),
                    "target_duration_sec (sec)": target.get("duration_sec"),
                    "target_packet_size_bytes (bytes)": target.get("packet_size_bytes"),
                    "target_packet_count (count)": target.get("packet_count"),
                    "sequence": sequence_str,
                    "sc_attempted_bps (bps)": parse_bps(sc.get("attempted_bps", "0")),
                    "sc_achieved_bps (bps)": bw_sc,
                    "sc_loss_rate_percent (%)": sc_loss,
                    "sc_interarrival (ms)": sc.get("interarrival time min/avg/max/mdev"),
                    "cs_attempted_bps (bps)": parse_bps(cs.get("attempted_bps", "0")),
                    "cs_achieved_bps (bps)": bw_cs,
                    "cs_loss_rate_percent (%)": cs_loss,
                    "cs_interarrival (ms)": cs.get("interarrival time min/avg/max/mdev"),
                    "avg_bandwidth (Mbps)": avg_bandwidth,
                    "available": available,
                    "failure_reason": failure_reason,
                    "data_quality": data_quality
                }

                rows.append(row)
            except Exception as e:
                print(f" Erreur parsing bandwidth (paths): {e}")
                continue

    elif "result" in data and isinstance(data["result"], dict):
        res = data["result"]
        sc = res.get("S->C results", {})
        cs = res.get("C->S results", {})
        target = data.get("target", {})

        dst_as = data.get("target_server", {}).get("ia") if data.get("target_server") else None

        
        if not sc and not cs:
            row = {
                "timestamp": timestamp,
                "src_as": src_as,
                "dst_as": dst_as,
                "path_fingerprint": None,
                "target_mbps (Mbps)": target.get("tier_mbps"),
                "target_duration_sec (sec)": target.get("duration_sec"),
                "target_packet_size_bytes (bytes)": target.get("packet_size_bytes"),
                "target_packet_count (count)": target.get("packet_count"),
                "sequence": None,
                "sc_attempted_bps (bps)": 0,
                "sc_achieved_bps (bps)": 0,
                "sc_loss_rate_percent (%)": 100.0,
                "sc_interarrival (ms)": None,
                "cs_attempted_bps (bps)": 0,
                "cs_achieved_bps (bps)": 0,
                "cs_loss_rate_percent (%)": 100.0,
                "cs_interarrival (ms)": None,
                "avg_bandwidth (Mbps)": 0.0,
                "available": 0,
                "failure_reason": "no_measurement_results",
                "data_quality": "failed"
            }
            rows.append(row)
            return rows

        # Safely parse loss rates
        sc_loss = safe_loss_rate(sc.get("loss_rate"))
        cs_loss = safe_loss_rate(cs.get("loss_rate"))
        avg_loss = (sc_loss + cs_loss) / 2

        # Parse bandwidth values safely
        bw_sc = parse_bps(sc.get("achieved_bps", "0"))
        bw_cs = parse_bps(cs.get("achieved_bps", "0"))
        
        if bw_sc == 0 and bw_cs == 0:
            data_quality = "failed"
            available = 0
            failure_reason = "zero_bandwidth_measured"
            avg_bandwidth = 0.0
        else:
            # Calculate average bandwidth safely
            if bw_sc > 0 and bw_cs > 0:
                avg_bandwidth = (bw_sc + bw_cs) / 2
            elif bw_sc > 0:
                avg_bandwidth = bw_sc
            elif bw_cs > 0:
                avg_bandwidth = bw_cs
            else:
                avg_bandwidth = 0.0
            
            # Determine data quality
            if avg_loss > 5:  # >5% loss
                data_quality = "degraded"
            else:
                data_quality = "good"
            
            available = 1
            failure_reason = None

        row = {
            "timestamp": timestamp,
            "src_as": src_as,
            "dst_as": dst_as,
            "path_fingerprint": None,
            "target_mbps (Mbps)": target.get("tier_mbps"),
            "target_duration_sec (sec)": target.get("duration_sec"),
            "target_packet_size_bytes (bytes)": target.get("packet_size_bytes"),
            "target_packet_count (count)": target.get("packet_count"),
            "sequence": None,
            "sc_attempted_bps (bps)": parse_bps(sc.get("attempted_bps", "0")),
            "sc_achieved_bps (bps)": bw_sc,
            "sc_loss_rate_percent (%)": sc_loss,
            "sc_interarrival (ms)": sc.get("interarrival time min/avg/max/mdev"),
            "cs_attempted_bps (bps)": parse_bps(cs.get("attempted_bps", "0")),
            "cs_achieved_bps (bps)": bw_cs,
            "cs_loss_rate_percent (%)": cs_loss,
            "cs_interarrival (ms)": cs.get("interarrival time min/avg/max/mdev"),
            "avg_bandwidth (Mbps)": avg_bandwidth,
            "available": available,
            "failure_reason": failure_reason,
            "data_quality": data_quality
        }

        rows.append(row)

    return rows

def parse_traceroute(data, timestamp):
    rows = []
    try:
        # Check if there's no path data
        if not data.get("path") or data.get("error"):
            row = {
                "timestamp": timestamp,
                "path_fingerprint": None,
                "hop_count (number)": 0,
                "src_as (address)": None,
                "dst_as (address)": None,
                "sequence (full sequence)": None,
                "global_rtt_sum (ms)": np.nan,
                "global_avg_rtt (ms)": np.nan,
                "available": 0,
                "failure_reason": data.get("error", "no_path_found"),
                "data_quality": "failed"
            }
            rows.append(row)
            return rows

        path = data["path"]
        fingerprint = path.get("fingerprint")
        hops = data.get("hops", [])
        
        # Ensure hops is not None
        if hops is None:
            hops = []
            
        hop_count = len(hops)

        sequence_str = path.get("sequence", "")
        formatted_sequence = format_sequence_with_ifaces(sequence_str) if sequence_str else ""

        sequence_parts = sequence_str.split() if sequence_str else []
        src_as = sequence_parts[0].split("#")[0] if sequence_parts else None
        dst_as = sequence_parts[-1].split("#")[0] if len(sequence_parts) > 0 else None

        hop_data = {}
        total_rtt_sum = 0
        total_rtt_count = 0
        
        for i, hop in enumerate(hops):
            if hop is None:
                continue
                
            rtts = hop.get("round_trip_times", [])
            if rtts is None:
                rtts = []
                
            avg_rtt = np.mean(rtts) if rtts else None
            total_rtt_sum += sum(rtts) if rtts else 0
            total_rtt_count += len(rtts) if rtts else 0
            
            hop_data.update({
                f"hop_{i}_isd_as": hop.get("isd_as"),
                f"hop_{i}_interface_id": hop.get("interface_id") or hop.get("interface"),
                f"hop_{i}_rtts_ms": rtts,
                f"hop_{i}_avg_rtt_ms": avg_rtt
            })

        global_avg_rtt = total_rtt_sum / total_rtt_count if total_rtt_count > 0 else None
        
        # Determine data quality
        data_quality = "good"
        if hop_count == 0:
            data_quality = "failed"
        elif global_avg_rtt and global_avg_rtt > 100:  # High latency
            data_quality = "degraded"

        row = {
            "timestamp": timestamp,
            "path_fingerprint": fingerprint,
            "hop_count (number)": hop_count,
            "src_as (address)": src_as,
            "dst_as (address)": dst_as,
            "sequence (full sequence)": formatted_sequence,
            "global_rtt_sum (ms)": total_rtt_sum,
            "global_avg_rtt (ms)": global_avg_rtt,
            "available": 1 if data_quality != "failed" else 0,
            "failure_reason": None if data_quality != "failed" else "traceroute_failed",
            "data_quality": data_quality,
            **hop_data
        }
        rows.append(row)

    except Exception as e:
        print(f"Erreur parsing traceroute: {e}")
        # Create failure entry for parsing errors
        row = {
            "timestamp": timestamp,
            "path_fingerprint": None,
            "hop_count (number)": 0,
            "src_as (address)": None,
            "dst_as (address)": None,
            "sequence (full sequence)": None,
            "global_rtt_sum (ms)": np.nan,
            "global_avg_rtt (ms)": np.nan,
            "available": 0,
            "failure_reason": f"parsing_error: {str(e)}",
            "data_quality": "failed"
        }
        rows.append(row)
    return rows

def parse_showpaths(data, timestamp):
    rows = []
    src_as = data.get("local_isd_as")
    dst_as = data.get("destination")
    
    # Check if no paths are available
    if not data.get("paths") or len(data.get("paths", [])) == 0:
        row = {
            "timestamp": timestamp,
            "src_as": src_as,
            "dst_as": dst_as,
            "path_fingerprint": None,
            "sequence": None,
            "mtu (bytes)": None,
            "path_status (1=alive,0=dead)": 0,
            "latency_raw (ns)": [],
            "avg_latency_ms (ms)": np.nan,
            "total_latency_ms (ms)": np.nan,
            "available": 0,
            "failure_reason": "no_paths_available",
            "data_quality": "failed"
        }
        rows.append(row)
        return rows

    # Process available paths
    for path in data.get("paths", []):
        latencies = path.get("latency", [])
        latency_filtered = [l for l in latencies if l >= 0]
        avg_latency = np.mean(latency_filtered) / 1e6 if latency_filtered else None
        total_latency = np.sum(latency_filtered) / 1e6 if latency_filtered else None

        sequence_str = path.get("sequence", "")
        formatted_sequence = format_sequence_with_ifaces(sequence_str)

        sequence_parts = sequence_str.split()
        src_as_path = sequence_parts[0].split("#")[0] if sequence_parts else src_as
        dst_as_path = sequence_parts[-1].split("#")[0] if sequence_parts else dst_as

        # Determine data quality
        path_alive = path.get("status") == "alive"
        data_quality = "good" if path_alive else "failed"
        if path_alive and avg_latency and avg_latency > 50:  # High latency
            data_quality = "degraded"

        row = {
            "timestamp": timestamp,
            "src_as": src_as_path,
            "dst_as": dst_as_path,
            "path_fingerprint": path.get("fingerprint"),
            "sequence": formatted_sequence,
            "mtu (bytes)": path.get("mtu"),
            "path_status (1=alive,0=dead)": 1 if path_alive else 0,
            "latency_raw (ns)": latencies,
            "avg_latency_ms (ms)": avg_latency,
            "total_latency_ms (ms)": total_latency,
            "available": 1 if path_alive else 0,
            "failure_reason": None if path_alive else "path_dead",
            "data_quality": data_quality
        }
        rows.append(row)
    return rows

def parse_path_changes(delta_dir):
    changes_detected = []

    for root, _, files in os.walk(delta_dir):
        for file in files:
            if file.startswith("delta_") and file.endswith(".json"):
                try:
                    with open(os.path.join(root, file)) as f:
                        data = json.load(f)

                    timestamp = data.get("timestamp")
                    src = data.get("source")
                    dst = data.get("destination")
                    change_status = data.get("change_status")

                    if change_status == "change_detected":
                        for change in data.get("changes", []):
                            fingerprint = change.get("fingerprint")
                            sequence_raw = change.get("sequence")
                            sequence = format_sequence_with_ifaces(sequence_raw) if sequence_raw else None
                            change_type = change.get("change")

                            changes_detected.append({
                                "timestamp": timestamp,
                                "source": src,
                                "destination": dst,
                                "change_type": change_type,
                                "path_fingerprint": fingerprint,
                                "sequence": sequence,
                                "available": 1,
                                "failure_reason": None,
                                "data_quality": "good"
                            })
                    elif change_status == "no_change":
                        # Add entry for no change detected (successful monitoring)
                        changes_detected.append({
                            "timestamp": timestamp,
                            "source": src,
                            "destination": dst,
                            "change_type": "no_change",
                            "path_fingerprint": None,
                            "sequence": None,
                            "available": 1,
                            "failure_reason": None,
                            "data_quality": "good"
                        })
                    elif change_status == "no_paths_present":
                        # Add entry for no paths situation
                        changes_detected.append({
                            "timestamp": timestamp,
                            "source": src,
                            "destination": dst,
                            "change_type": "no_paths",
                            "path_fingerprint": None,
                            "sequence": None,
                            "available": 0,
                            "failure_reason": "no_paths_present",
                            "data_quality": "failed"
                        })

                except Exception as e:
                    print(f"Error parsing delta file {file}: {e}")

    return changes_detected

def fill_missing_measurements(df_showpaths, df_ping, df_traceroute):
    """Fill missing ping and traceroute measurements based on showpaths schedule"""
    
    if df_showpaths.empty:
        print("No showpaths data available - cannot determine expected measurement schedule")
        return df_ping, df_traceroute
    
    # Convert timestamps to datetime
    df_showpaths['timestamp'] = pd.to_datetime(df_showpaths['timestamp'])
    if not df_ping.empty:
        df_ping['timestamp'] = pd.to_datetime(df_ping['timestamp'])
    if not df_traceroute.empty:
        df_traceroute['timestamp'] = pd.to_datetime(df_traceroute['timestamp'])
    
    # Get all expected measurement times and src-dst pairs from showpaths
    expected_schedule = df_showpaths[['timestamp', 'src_as', 'dst_as']].drop_duplicates()
    
    # Fill missing ping measurements
    if not df_ping.empty:
        ping_existing = df_ping[['timestamp', 'src_as', 'dst_as']].drop_duplicates()
        ping_expected = expected_schedule.copy()
        ping_expected.columns = ['timestamp', 'src_as', 'dst_as']
        
        # Find missing ping measurements
        ping_merged = ping_expected.merge(ping_existing, on=['timestamp', 'src_as', 'dst_as'], how='left', indicator=True)
        ping_missing = ping_merged[ping_merged['_merge'] == 'left_only'][['timestamp', 'src_as', 'dst_as']]
        
        # Create missing ping entries
        missing_ping_rows = []
        for _, row in ping_missing.iterrows():
            missing_ping_rows.append({
                "timestamp": row['timestamp'],  
                "src_as": row['src_as'],
                "dst_as": row['dst_as'],
                "path_fingerprint": None,
                "sequence": None,
                "sent (count)": 0,
                "received (count)": 0,
                "loss_rate (%)": 100.0,
                "min_rtt (ms)": np.nan,
                "avg_rtt (ms)": np.nan,
                "max_rtt (ms)": np.nan,
                "mdev_rtt (ms)": np.nan,
                "replies_rtt (ms)": [],
                "available": 0,
                "failure_reason": "no_measurement_file_generated",
                "data_quality": "failed"
            })
        
        if missing_ping_rows:
            df_missing_ping = pd.DataFrame(missing_ping_rows)
            df_ping = pd.concat([df_ping, df_missing_ping], ignore_index=True)
            print(f"Added {len(missing_ping_rows)} missing ping measurements")
    else:
        # If no ping data exists, create entries for all expected times
        missing_ping_rows = []
        for _, row in expected_schedule.iterrows():
            missing_ping_rows.append({
                "timestamp": row['timestamp'],
                "src_as": row['src_as'],
                "dst_as": row['dst_as'],
                "path_fingerprint": None,
                "sequence": None,
                "sent (count)": 0,
                "received (count)": 0,
                "loss_rate (%)": 100.0,
                "min_rtt (ms)": np.nan,
                "avg_rtt (ms)": np.nan,
                "max_rtt (ms)": np.nan,
                "mdev_rtt (ms)": np.nan,
                "replies_rtt (ms)": [],
                "available": 0,
                "failure_reason": "no_measurement_file_generated",
                "data_quality": "failed"
            })
        
        if missing_ping_rows:
            df_ping = pd.DataFrame(missing_ping_rows)
            print(f"Created {len(missing_ping_rows)} missing ping measurements (no ping files found)")
    
    # Fill missing traceroute measurements
    if not df_traceroute.empty:
        tr_existing = df_traceroute[['timestamp', 'src_as (address)', 'dst_as (address)']].drop_duplicates()
        tr_expected = expected_schedule.copy()
        tr_expected.columns = ['timestamp', 'src_as (address)', 'dst_as (address)']
        
        # Find missing traceroute measurements
        tr_merged = tr_expected.merge(tr_existing, on=['timestamp', 'src_as (address)', 'dst_as (address)'], how='left', indicator=True)
        tr_missing = tr_merged[tr_merged['_merge'] == 'left_only'][['timestamp', 'src_as (address)', 'dst_as (address)']]
        
        # Create missing traceroute entries
        missing_tr_rows = []
        for _, row in tr_missing.iterrows():
            missing_tr_rows.append({
                "timestamp": row['timestamp'],  
                "path_fingerprint": None,
                "hop_count (number)": 0,
                "src_as (address)": row['src_as (address)'],
                "dst_as (address)": row['dst_as (address)'],
                "sequence (full sequence)": None,
                "global_rtt_sum (ms)": np.nan,
                "global_avg_rtt (ms)": np.nan,
                "available": 0,
                "failure_reason": "no_measurement_file_generated",
                "data_quality": "failed"
            })
        
        if missing_tr_rows:
            df_missing_tr = pd.DataFrame(missing_tr_rows)
            df_traceroute = pd.concat([df_traceroute, df_missing_tr], ignore_index=True)
            print(f"Added {len(missing_tr_rows)} missing traceroute measurements")
    else:
        # If no traceroute data exists, create entries for all expected times
        missing_tr_rows = []
        for _, row in expected_schedule.iterrows():
            missing_tr_rows.append({
                "timestamp": row['timestamp'],
                "path_fingerprint": None,
                "hop_count (number)": 0,
                "src_as (address)": row['src_as'],
                "dst_as (address)": row['dst_as'],
                "sequence (full sequence)": None,
                "global_rtt_sum (ms)": np.nan,
                "global_avg_rtt (ms)": np.nan,
                "available": 0,
                "failure_reason": "no_measurement_file_generated",
                "data_quality": "failed"
            })
        
        if missing_tr_rows:
            df_traceroute = pd.DataFrame(missing_tr_rows)
            print(f"Created {len(missing_tr_rows)} missing traceroute measurements (no traceroute files found)")
    
    return df_ping, df_traceroute

def collect_all_data(base_path):
    all_ping = []
    all_bandwidth = []
    all_traceroute = []
    all_showpaths = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                # Skip delta files (processed separately) and mp-prober files
                if file.startswith("delta_") or file.startswith("mp-prober"):
                    continue
                    
                fpath = os.path.join(root, file)
                file_ts = extract_timestamp_from_filename(file).isoformat()
                try:
                    with open(fpath) as f:
                        data = json.load(f)

                    src_as = data.get("ia") or data.get("as") or data.get("local_isd_as")

                    # Check for ping files first
                    if "probes" in data and any("ping_result" in probe for probe in data.get("probes", [])):
                        parsed = parse_ping(data, src_as)
                        all_ping.extend(parsed)

                    # Check for bandwidth files (including error cases)
                    elif ("target_mbps" in data or 
                          (data.get("error") and ("no paths found" in data.get("error", "").lower() or 
                                                "failed to retrieve paths" in data.get("error", "").lower())) or
                          ("paths" in data and any(
                              "result" in path and ("S->C results" in path["result"] or "C->S results" in path["result"])
                              for path in data.get("paths", [])
                          )) or
                          ("result" in data and isinstance(data["result"], dict) and 
                           ("S->C results" in data["result"] or "C->S results" in data["result"]))):
                        parsed = parse_bandwidth(data, src_as)
                        all_bandwidth.extend(parsed)

                    # Check for traceroute files
                    elif "hops" in data:
                        parsed = parse_traceroute(data, file_ts)
                        all_traceroute.extend(parsed)

                    # Check for showpaths files
                    elif "local_isd_as" in data and "destination" in data:
                        parsed = parse_showpaths(data, file_ts)
                        all_showpaths.extend(parsed)

                    # If none of the above, log unrecognized file
                    else:
                        print(f"Unrecognized file format: {fpath}")
                        print(f"   Keys: {list(data.keys())}")

                except Exception as e:
                    print(f"Error parsing file {fpath}: {e}")

    return all_ping, all_bandwidth, all_traceroute, all_showpaths

def save_dfs(base_path, output_dir="./scionpathml/transformers/datasets"):
    os.makedirs(output_dir, exist_ok=True)

    ping, bandwidth, traceroute, showpaths = collect_all_data(base_path)

    # Create DataFrames
    df_ping = pd.DataFrame(ping) if ping else pd.DataFrame()
    df_bandwidth = pd.DataFrame(bandwidth) if bandwidth else pd.DataFrame()
    df_traceroute = pd.DataFrame(traceroute) if traceroute else pd.DataFrame()
    df_showpaths = pd.DataFrame(showpaths) if showpaths else pd.DataFrame()

    # Fill missing measurements based on showpaths schedule
    df_ping_complete, df_traceroute_complete = fill_missing_measurements(df_showpaths, df_ping, df_traceroute)

    # Convert timestamps back to strings for CSV output and sort
    if not df_ping_complete.empty:
        df_ping_complete['timestamp'] = df_ping_complete['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        df_ping_complete = df_ping_complete.sort_values("timestamp")
        df_ping_complete.to_csv(os.path.join(output_dir, "data_PG.csv"), index=False)
        original_count = len(df_ping) if not df_ping.empty else 0
        total_count = len(df_ping_complete)
        missing_count = total_count - original_count
        print(f"Saved {total_count} ping entries ({original_count} original + {missing_count} filled missing)")

    if not df_bandwidth.empty:
        df_bandwidth = df_bandwidth.sort_values("timestamp")
        df_bandwidth.to_csv(os.path.join(output_dir, "data_BW.csv"), index=False)
        print(f"Saved {len(df_bandwidth)} bandwidth entries (including {len(df_bandwidth[df_bandwidth['available']==0])} failures)")

    if not df_traceroute_complete.empty:
        df_traceroute_complete['timestamp'] = df_traceroute_complete['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        df_traceroute_complete = df_traceroute_complete.sort_values("timestamp")
        df_traceroute_complete.to_csv(os.path.join(output_dir, "data_TR.csv"), index=False)
        original_count = len(df_traceroute) if not df_traceroute.empty else 0
        total_count = len(df_traceroute_complete)
        missing_count = total_count - original_count
        print(f"Saved {total_count} traceroute entries ({original_count} original + {missing_count} filled missing)")

    if not df_showpaths.empty:
        df_showpaths = df_showpaths.sort_values("timestamp")
        df_showpaths.to_csv(os.path.join(output_dir, "data_SP.csv"), index=False)
        print(f"Saved {len(df_showpaths)} showpaths entries (including {len(df_showpaths[df_showpaths['available']==0])} failures)")

    delta_changes = parse_path_changes(base_path)
    if delta_changes:
        df_changes = pd.DataFrame(delta_changes).sort_values("timestamp")
        df_changes.to_csv(os.path.join(output_dir, "data_CP.csv"), index=False)
        print(f"Saved {len(df_changes)} path change entries (including {len(df_changes[df_changes['available']==0])} failures)")

    # Print quality statistics
    print("\nData Quality Statistics:")
    print("-" * 50)
    
    if not df_ping_complete.empty:
        total_ping = len(df_ping_complete)
        successful_ping = len(df_ping_complete[df_ping_complete['available']==1])
        missing_ping = len(df_ping_complete[df_ping_complete['failure_reason']=='no_measurement_file_generated'])
        success_rate = (successful_ping / total_ping) * 100
        print(f"Ping: {success_rate:.1f}% success rate ({successful_ping}/{total_ping})")
        print(f"      {missing_ping} measurements had no files (complete failures)")
    
    if not df_bandwidth.empty:
        success_rate = (len(df_bandwidth[df_bandwidth['available']==1]) / len(df_bandwidth)) * 100
        print(f"Bandwidth: {success_rate:.1f}% success rate")
    
    if not df_traceroute_complete.empty:
        total_tr = len(df_traceroute_complete)
        successful_tr = len(df_traceroute_complete[df_traceroute_complete['available']==1])
        missing_tr = len(df_traceroute_complete[df_traceroute_complete['failure_reason']=='no_measurement_file_generated'])
        success_rate = (successful_tr / total_tr) * 100
        print(f"Traceroute: {success_rate:.1f}% success rate ({successful_tr}/{total_tr})")
        print(f"           {missing_tr} measurements had no files (complete failures)")
    
    if not df_showpaths.empty:
        success_rate = (len(df_showpaths[df_showpaths['available']==1]) / len(df_showpaths)) * 100
        print(f"Showpaths: {success_rate:.1f}% success rate")
    
    if delta_changes:
        success_rate = (len(df_changes[df_changes['available']==1]) / len(df_changes)) * 100
        print(f"Path Changes: {success_rate:.1f}% success rate")
        
        change_types = df_changes['change_type'].value_counts()
        print(f"\nPath Change Types:")
        for change_type, count in change_types.items():
            print(f"  {change_type}: {count}")
