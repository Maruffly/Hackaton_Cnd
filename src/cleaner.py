import pandas as pd
import ipaddress
import os

def is_private_ip(ip):
    """Check if network is private - RFC 1918"""
    try:
        # Convert object to an object : use private property
        return ipaddress.ip_address(ip).is_private
    except:
        return False

def process_firewall_logs(input_path, output_dir):
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
        'dst_port', 'action', 'reason', 'user'
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
        # --- STEP A : Cleaning ---
        # Clean NA
        chunk = chunk.dropna(subset=['src_ip', 'dst_ip', 'src_port', 'dst_port', 'timestamp']).copy()
        chunk['src_port'] = chunk['src_port'].astype('uint16')
        chunk['dst_port'] = chunk['dst_port'].astype('uint16')

        chunk['user'] = chunk['user'].fillna('system_process')
        chunk = chunk.dropna(subset=['src_ip', 'dst_ip', 'timestamp'])

        # --- STEP B :False positive detection ---
        mask_src_internal = chunk['src_ip'].apply(is_private_ip)
        mask_dst_internal = chunk['dst_ip'].apply(is_private_ip)

        chunk['is_false_positive'] = (
            (mask_src_internal == True) & 
            (mask_dst_internal == True) & 
            (chunk['action'] == 'DENY') & 
            (chunk['reason'] == 'Protocol violation')
        )

        # --- STEP C : EXPORT ---
        output_file = os.path.join(output_dir, f"firewall_part_{i+1}.csv")
        chunk.to_csv(output_file, index=False)
        
        print(f"Chunk {i+1} finish and saved at {output_file}")

if __name__ == "__main__":
    # Test parameters
    FILE_NAME = "firewall_logs_100mb_nov2025.csv"
    OUTPUT_FOLDER = "data/processed_chunks"
    
    process_firewall_logs(FILE_NAME, OUTPUT_FOLDER)