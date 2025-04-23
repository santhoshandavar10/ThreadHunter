import os
import json
import time
import config
from utils import hash_file, check_virustotal

HASH_DB = "hash_store.json"
LOG_FILE = "security_log.txt"

# Load stored hashes
if os.path.exists(HASH_DB):
    with open(HASH_DB, "r") as f:
        known_hashes = json.load(f)
else:
    known_hashes = {}

def log_event(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()}: {message}\n")

def scan():
    print("🔍 Scanning folder...")
    for root, dirs, files in os.walk(config.FOLDER_TO_MONITOR):
        for file in files:
            path = os.path.join(root, file)
            try:
                file_hash = hash_file(path)
                if path not in known_hashes:
                    known_hashes[path] = file_hash
                    result = check_virustotal(file_hash)
                    if result and result.get("malicious", 0) > 0:
                        log_event(f"⚠️ Malware Detected: {file} — {result}")
                    else:
                        log_event(f"✅ New File Safe: {file}")
                elif known_hashes[path] != file_hash:
                    log_event(f"⚠️ File Modified: {file}")
                    known_hashes[path] = file_hash
            except Exception as e:
                log_event(f"❌ Error scanning {file}: {e}")

    # Save updated hash list
    with open(HASH_DB, "w") as f:
        json.dump(known_hashes, f)

if __name__ == "__main__":
    while True:
        scan()
        time.sleep(60)  # Scan every 60 seconds
