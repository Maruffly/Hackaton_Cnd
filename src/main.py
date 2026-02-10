import os
import logging
import shutil
import glob
import json
from datetime import datetime
from cleaner import process_firewall_logs


RAW_DIR = "data/raw"
ARCHIVE_DIR = "data/archive"
PROCESSED_DIR = "data/processed"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"), # Save into file
        logging.StreamHandler()              # Console display
    ]
)

def run_pipeline():
	summary_stats = {
        "timestamp": datetime.now().isoformat(),
        "files_processed": 0,
        "total_alerts": 0,
        "detections_by_type": {
            "false_positives": 0,
            "reconnaissance": 0,
            "lateral_movement": 0
        }
    }
	# Create folder if not exist
	for folder in [RAW_DIR, PROCESSED_DIR, ARCHIVE_DIR]:
		os.makedirs(folder, exist_ok=True)

	# List all CSV in RAW folder
	files_to_process = glob.glob(os.path.join(RAW_DIR, "*.csv"))
	if not files_to_process:
		print(f"No files to process in {RAW_DIR}")
		return
	for file_path in files_to_process:
		file_name = os.path.basename(file_path)
		print(f"=== Start process files in  : {file_name}")

		try:
			# Execute cleaner & create subfolder to store chunks
			current_output_dir = os.path.join(PROCESSED_DIR, file_name.replace('.csv', ''))
			metrics = process_firewall_logs(file_path, current_output_dir)\
	
			# Update global report
			summary_stats["files_processed"] += 1
			summary_stats["detections_by_type"]["false_positives"] += metrics.get("fp", 0)
			summary_stats["detections_by_type"]["reconnaissance"] += metrics.get("recon", 0)
			summary_stats["detections_by_type"]["lateral_movement"] += metrics.get("lateral", 0)
			summary_stats["total_alerts"] += (metrics.get("recon", 0) + metrics.get("lateral", 0))
	
			# Secured archive
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			archive_path = os.path.join(ARCHIVE_DIR, f"{timestamp}_{file_name}")

			# Move original RAW file to Archive
			shutil.move(file_path, archive_path)
			print(f"Success : {file_name} archived in path : {archive_path}")

		except Exception as e:
			# If a file is corrupted : log error and continue exec
			print(f"Error on {file_name} : {e}")

	# SAVE FINAL REPORT
	report_path = os.path.join(PROCESSED_DIR, "simulation_report.json")
	with open(report_path, "w") as f:
		json.dump(summary_stats, f, indent=4)
	print(f"\n[OBSERVABILITÉ] Rapport généré : {report_path}")

if __name__ == "__main__":
	run_pipeline()
