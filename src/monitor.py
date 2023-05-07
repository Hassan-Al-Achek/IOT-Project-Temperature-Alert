import os
import time
import subprocess


def monitor_directory(directory, script_path, script_args):
    # Get the initial list of files in the directory
    initial_files = set(os.listdir(directory))

    while True:
        # Get the current list of files in the directory
        current_files = set(os.listdir(directory))

        # Find the new files in the directory
        new_files = current_files - initial_files

        for file_name in new_files:
            if file_name.startswith("temp_") and file_name.endswith("_metrics.csv"):
                print("[~] Running")
                subprocess.run(["python", script_path, script_args[0], script_args[1]])
                initial_files = current_files
                print("[+] Data Updated")

        # Sleep for a short time before checking the directory again
        time.sleep(1)


monitor_directory("../result", ".\\core.py", ["-d", "../result"])
