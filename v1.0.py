import json
from farmbot import Farmbot, FarmbotToken

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
with open("plant_coords.json", "r") as f:
    plant_coords = json.load(f)

class MyHandler:
    def on_connect(self, bot, mqtt_client):
        for plant in plant_coords:
            x, y, z = plant["x"], plant["y"], plant["z"]
            request_id = bot.move_absolute(x, y, z)
            print(f"Moving to plant at ({x}, {y}, {z}). Request ID: {request_id}")
            request_id = bot.take_photo()
            print(f"Taking photo. Request ID: {request_id}")

    def on_change(self, bot, state):
        pass

    def on_log(self, bot, log):
        print(f"Log: {log['message']}")

    def on_response(self, bot, response):
        print(f"Successful request: {response.id}")

    def on_error(self, bot, response):
        print(f"Failed request: {response.id}, Errors: {response.errors}")

# Connect to FarmBot with the custom handler
handler = MyHandler()
fb.connect(handler)