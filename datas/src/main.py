import os
import shutil
import glob
from datetime import datetime
from cleaner import process_firewall_logs


RAW_DIR = "data/raw"
ARCHIVE_DIR = "data/archive"
PROCESSED_DIR = "data/processed"

def run_pipeline():
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
			process_firewall_logs(file_path, current_output_dir)

			# Secured archive
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			archive_path = os.path.join(ARCHIVE_DIR, f"{timestamp}_{file_name}")

			# Move original RAW file to Archive
			shutil.move(file_path, archive_path)
			print(f"Success : {file_name} archived in path : {archive_path}")

		except Exception as e:
			# If a file is corrupted : log error but continue the program
			print(f"Error on {file_name} : {e}")

if __name__ == "__main__":
	run_pipeline()
