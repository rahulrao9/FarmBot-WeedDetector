import json
import threading
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
with open("locations.json", "r") as f:
    plant_coords = json.load(f)

class MoveHandler:
    def __init__(self, next_handler, event):
        self.next_handler = next_handler
        self.event = event

    def on_connect(self, bot, mqtt_client):
        if plant_coords:
            self.move_next(bot)

    def move_next(self, bot):
        if plant_coords:
            plant = plant_coords.pop(0)
            x, y, z = plant["x"], plant["y"], plant["z"]
            request_id = bot.move_absolute(x, y, z)
            print(f"Moving to plant at ({x}, {y}, {z}). Request ID: {request_id}")

    def on_change(self, bot, state):
        pass

    def on_log(self, bot, log):
        print(f"Log: {log['message']}")

    def on_response(self, bot, response):
        print(f"Successful request: {response.id}")
        self.event.set()  # Signal that the move operation is complete

    def on_error(self, bot, response):
        print(f"Failed request: {response.id}, Errors: {response.errors}")
        self.event.set()  # Signal that the move operation is complete

class PhotoHandler:
    def __init__(self, move_handler, event):
        self.move_handler = move_handler
        self.event = event

    def on_connect(self, bot, mqtt_client):
        if plant_coords:
            self.take_photo(bot)

    def take_photo(self, bot):
        request_id = bot.take_photo()
        print(f"Taking photo. Request ID: {request_id}")

    def on_change(self, bot, state):
        pass

    def on_log(self, bot, log):
        print(f"Log: {log['message']}")

    def on_response(self, bot, response):
        print(f"Successful request: {response.id}")
        # After taking the photo, move to the next plant
        if plant_coords:
            self.move_handler.event.clear()
            bot._handler = self.move_handler
            threading.Thread(target=self.move_handler.move_next, args=(bot,)).start()
            self.move_handler.event.wait()  # Wait for the move operation to complete
            bot._handler = self

    def on_error(self, bot, response):
        print(f"Failed request: {response.id}, Errors: {response.errors}")
        # After taking the photo, move to the next plant
        if plant_coords:
            self.move_handler.event.clear()
            bot._handler = self.move_handler
            threading.Thread(target=self.move_handler.move_next, args=(bot,)).start()
            self.move_handler.event.wait()  # Wait for the move operation to complete
            bot._handler = self

# Instantiate handlers and event
event = threading.Event()
move_handler = MoveHandler(None, event)
photo_handler = PhotoHandler(move_handler, event)
move_handler.next_handler = photo_handler

# Connect to FarmBot with the move handler
fb.connect(move_handler)
