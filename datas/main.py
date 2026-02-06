import pandas as pd
import os

INPUT_FILE = "firewall_logs_100mb_nov2025.csv"
OUTPUT_DIR = "data/processed_chunks"

os.makedirs(OUTPUT_DIR, exist_ok=True)