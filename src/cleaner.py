import pandas as pd
import ipaddress
import os
from utils import is_private_ip
from utils import is_multicast_broadcast
from db import write_chunk_to_db

def process_firewall_logs(input_path, output_dir, db_engine=None, db_table="firewall_logs"):
    # Init metrics
    file_metrics = {
        "lines": 0,
        "fp": 0,
        "recon": 0,
        "lateral": 0
    }

    # Convert to type to save RAM
    dtype_spec = {
        'firewall_id': 'category',
        'protocol': 'category',
        'action': 'category',
        'reason': 'category',
    }
    
    # Only use relevant columns
    cols_needed = [
        'timestamp', 'src_ip', 'dst_ip', 'src_port', 
        'dst_port', 'action', 'reason', 'user', 'protocol'
    ]

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Read chunks
    chunk_size = 100000
    reader = pd.read_csv(
        input_path, 
        chunksize=chunk_size,
        dtype=dtype_spec,
        usecols=cols_needed,
        parse_dates=['timestamp']
    )

    print(f"Processing treatment...")

    for i, chunk in enumerate(reader):
        #=== STEP A : Cleaning ===
        ## Clean NA
        chunk = chunk.dropna(subset=['src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp']).copy()
        chunk['src_port'] = chunk['src_port'].astype('uint16')
        chunk['dst_port'] = chunk['dst_port'].astype('uint16')

        chunk['user'] = chunk['user'].fillna('system_process')
        chunk = chunk.dropna(subset=['src_ip', 'dst_ip', 'timestamp'])

        #=== STEP B :False positive detection ===
        ## Check if internal connections
        is_src_internal = chunk['src_ip'].apply(is_private_ip)
        is_dst_internal = chunk['dst_ip'].apply(is_private_ip)
        is_noise_dst = chunk['dst_ip'].apply(is_multicast_broadcast)

        chunk['is_false_positive'] = (
            ### A : Internal broadcast/multicast
            (is_src_internal & is_noise_dst) |
 
            ### B : Protocol error : service known to be blocked
            (is_src_internal & is_dst_internal & (chunk['reason'] == 'Protocol violation')) |

            ### C : Internal ping bloqued (monitoring noise)
            (is_src_internal & is_dst_internal & (chunk['protocol'] == 'ICMP')))

        # === STEP C : CREATE DETECTION COLUMNS ===
        # Reconnaissance: external -> internal on uncommon ports
        chunk['is_scan'] = (~is_src_internal & is_dst_internal & (chunk['dst_port'] < 1024))
        
        # Lateral movement: internal -> internal suspicious traffic
        chunk['is_lateral'] = (is_src_internal & is_dst_internal & (chunk['action'] == 'DENY'))
        
        # Noise: broadcast/multicast
        chunk['is_noise'] = is_noise_dst

        #=== STEP D : Update file counters ===
        file_metrics["lines"] += len(chunk)
        file_metrics["fp"] += int(chunk['is_false_positive'].sum())
        file_metrics["recon"] += int(chunk['is_scan'].sum())
        file_metrics["lateral"] += int(chunk['is_lateral'].sum())

        #===STEP E : EXPORT ===
        output_file = os.path.join(output_dir, f"firewall_part_{i+1}.csv")
        chunk.to_csv(output_file, index=False)

        #===STEP F : DATABASE INSERT ===
        write_chunk_to_db(chunk, db_engine, db_table)

        print(f"Chunk {i+1} finish and saved at {output_file}")
    return file_metrics

if __name__ == "__main__":
    # Test parameters
    FILE_NAME = "firewall_logs_100mb_nov2025.csv"
    OUTPUT_FOLDER = "data/processed_chunks"
    
    process_firewall_logs(FILE_NAME, OUTPUT_FOLDER)
