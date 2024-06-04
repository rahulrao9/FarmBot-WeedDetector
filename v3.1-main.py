from v3dot1 import run
import multiprocessing
import json
import time
import signal

# Load plant coordinates from a JSON file
with open("locations.json", "r") as f:
    PLANTCOORDINATES = json.load(f)

if __name__ == "__main__":
    creds = "credentials.json"

    for location in PLANTCOORDINATES:
        p = multiprocessing.Process(target=run, args=[creds, location, "move"])
        p.start()
        time.sleep(15)
        p.terminate()
        print(f"process terminated {location}")

        p = multiprocessing.Process(target=run, args=[creds, location, "photo"])
        p.start()
        time.sleep(10)
        p.terminate()
        print(f"process terminated {location}")