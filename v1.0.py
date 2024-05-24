import argparse
import json
from farmbot import Farmbot, StubHandler

# Define a custom handler to save photos
class PhotoHandler(StubHandler):
    def on_response(self, bot, response):
        if isinstance(response, OkResponse):
            print(f"Photo taken successfully at {response.id}")

    def on_error(self, bot, response):
        print(f"Error occurred: {response.errors}")

# Function to read plant locations from a file
def read_locations(file_path):
    with open(file_path, 'r') as file:
        locations = json.load(file)
    return locations

# Function to move to each location and take a photo
def take_photos(farmbot, locations):
    handler = PhotoHandler()
    farmbot.connect(handler)
    for loc in locations:
        x, y, z = loc['x'], loc['y'], loc['z']
        farmbot.move_absolute(x, y, z)
        farmbot.take_photo()
    farmbot.disconnect()

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description='Move FarmBot to each plant location and take a photo.')
    parser.add_argument('email', type=str, help='Email for FarmBot login')
    parser.add_argument('password', type=str, help='Password for FarmBot login')
    parser.add_argument('locations_file', type=str, help='Path to the JSON file containing plant locations')
    args = parser.parse_args()

    # Login to FarmBot
    farmbot = Farmbot.login(email=args.email, password=args.password)
    
    # Read locations from file
    locations = read_locations(args.locations_file)
    
    # Take photos at each location
    take_photos(farmbot, locations)

if __name__ == '__main__':
    main()
