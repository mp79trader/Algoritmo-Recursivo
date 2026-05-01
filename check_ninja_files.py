import os
import time
from datetime import datetime

exchange_dir = r"C:\QuantumGAN\Exchange"

print(f"Checking files in {exchange_dir}...")

if os.path.exists(exchange_dir):
    files = os.listdir(exchange_dir)
    for f in files:
        full_path = os.path.join(exchange_dir, f)
        mtime = os.path.getmtime(full_path)
        dt_mtime = datetime.fromtimestamp(mtime)
        age_seconds = time.time() - mtime
        age_minutes = age_seconds / 60
        
        print(f"File: {f}")
        print(f"  Modified: {dt_mtime}")
        print(f"  Age: {age_minutes:.2f} minutes")
        print("-" * 30)
else:
    print("Exchange directory does not exist!")
