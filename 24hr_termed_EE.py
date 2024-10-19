import requests
import json
from datetime import datetime, timedelta

from pandas.io import json

# API Key
secret_file = 'C:\\Users\\logan.fryer\\OneDrive - PACS\\Documents\\Misc\\my_api_key.txt'
with open(secret_file, "r") as f:
    secret_key = f.read().strip()
    f.close()

# static variables
domain = 'https://pacs.freshservice.com'
api_key = secret_key
password = 'x'
group_id = 21000561314

# need to pull the last 24 hrs worth of termed EE's, get the ID and serperation date and push to an excel file

# # create time stamp for updated_since
# now = datetime.utcnow()
# updated_since = (now - timedelta(hours=24)).isoformat() + 'Z'

# get tickets
url = f'{domain}/api/v2/tickets'
headers = {'Content-Type': 'application/json'}
params = {
    # 'updated_since': updated_since,
    'group_id': group_id,
    # 'status': 5
}


response = requests.get(url, auth=(api_key, password), headers=headers, data=params)

if response.status_code == 200:
    try:
        response_data = response.json()
        tickets = response_data['tickets']
        # ticket_id = tickets[0]['id']
        # ticket_subject = tickets[0]['subject']


        for tickets in response_data:
            print(f"ticket id: {tickets['id']}, Subject: {tickets['subject']}")

    except json.JSONDecodeError:
        print(f"error decoding json response: {response.text}")
else:
    print(f"error fetching tickets: {response.status_code}")

