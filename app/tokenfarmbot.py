import json
from getpass import getpass
import requests
from farmbot import FarmbotToken
from getpass import getpass


# inputs
SERVER = input("https://my.farm.bot")
EMAIL = input("skanda03prasad@gmail.com")
PASSWORD = getpass("shaarvarp")

# get your FarmBot authorization token
headers = {'content-type': 'application/json'}
user = {'user': {'email': EMAIL, 'password': PASSWORD}}
response = requests.post(f'{SERVER}/api/tokens',
                         headers=headers, json=user)
TOKEN = response.json()
print(f'{TOKEN = }')

# # TOKEN = ...

# headers = {'Authorization': 'Bearer ' + TOKEN['token']['encoded'],
#            'content-type': "application/json"}
# response = requests.get(f'https:{TOKEN['token']['unencoded']['iss']}/api/points', headers=headers)
# points = response.json()
# print(json.dumps(points, indent=2))