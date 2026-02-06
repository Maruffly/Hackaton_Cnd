import pandas as pd
import ipaddress
import os

def process_firewall_logs(input_path, output_dir):
	# Def type to save RAM
	dtype_spec = {
		'firewall_id': 'category',
		'protocol': 'category',
		'reason': 'category',
		'src_port': 'uint16',
		'dst_port': 'uint16'
	}
	reader = pd.read_csv(input_path, chunksize=chunk_size,
			dtype=dtype_spec, parse_dates=['timestamp'], usecols=['src_port', 'dst_port'])
	


	for i, chunk in enumerate(reader):
		# Clean NULLs
		chunk = chunk.dropna(subset=['src_ip', 'dst_ip', 'timestamp'])
		is_internal_src = chunk
		# Detect false positives
		chunk = identify_false_positives(chunk)
		# Export 100MB chunks
