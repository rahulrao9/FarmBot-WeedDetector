import json
import time
from farmbot import Farmbot, FarmbotToken

class MoveHandler:
    def __init__(self, plant):
        self.plant = plant
        self.done = False  # Initialize done attribute

    def on_connect(self, bot, mqtt_client):
        x, y, z = self.plant["x"], self.plant["y"], self.plant["z"]
        request_id = bot.move_absolute(x, y, z)
        print(f"Moving to plant at ({x}, {y}, {z}). Request ID: {request_id}")

    def on_change(self, bot, state):
        pass

    def on_log(self, bot, log):
        print(f"Log: {log['message']}")

    def on_response(self, bot, response):
        print(f"Successful request: {response.id}")
        self.done = True  # Set done to True

    def on_error(self, bot, response):
        print(f"Failed request: {response.id}, Errors: {response.errors}")
        self.done = True  # Set done to True

class PhotoHandler:
    def __init__(self):
        self.done = False  # Initialize done attribute

    def on_connect(self, bot, mqtt_client):
        request_id = bot.take_photo()
        print(f"Taking photo. Request ID: {request_id}")

    def on_change(self, bot, state):
        pass

    def on_log(self, bot, log):
        print(f"Log: {log['message']}")

    def on_response(self, bot, response):
        print(f"Successful request: {response.id}")
        self.done = True  # Set done to True

    def on_error(self, bot, response):
        print(f"Failed request: {response.id}, Errors: {response.errors}")
        self.done = True  # Set done to True


def main():
    # Load credentials from a JSON file
    with open("credentials.json", "r") as f:
        creds = json.load(f)
        email = creds["email"]
        password = creds["password"]
        server = creds["server"]

    # Download token and create FarmBot instance
    raw_token = FarmbotToken.download_token(email, password, server)
    fb = Farmbot(raw_token)

    # Load plant coordinates from a JSON file
    with open("locations.json", "r") as f:
        plant_coords = json.load(f)

    for plant in plant_coords:
        # Move to the plant
        mover = MoveHandler(plant)
        fb.connect(mover)
        
        # Wait for move to complete
        while not mover.done:
            time.sleep(1)
            print("still in mover while")
        fb.disconnect()
        
        # Take photo at the plant
        phototaker = PhotoHandler()
        fb.connect(phototaker)
        
        # Wait for photo to complete
        while not phototaker.done:
            time.sleep(1)
            print("entered phototaker while")
        fb.disconnect()


if __name__ == "__main__":
    main()
