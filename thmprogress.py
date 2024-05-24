import requests
import matplotlib.pyplot as plt
import json

# Get your SID cookie and replace RANDOM_SID with it.
cookies = {
    "connect.sid": "RANDOM_SID",
}

# Fetch data from the API (0day has most rooms complete so we use his profile)
url = "https://tryhackme.com/api/all-completed-rooms?username=0day&limit=1000&page=1"
response = requests.get(url)
rooms_data = response.json()

# Extract all the room codes
room_codes = [room['code'] for room in rooms_data]

room_codes_str = "%2C".join(room_codes)

url = f"https://tryhackme.com/api/v2/hacktivities/search-progress?roomCodes={room_codes_str}"

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.5",
    "priority": "u=1, i",
}

response = requests.get(url, headers=headers, cookies=cookies)
progress_data = response.json()

# Extract the correct data based on the actual response structure
if 'data' in progress_data and 'roomProgress' in progress_data['data']:
    progress_data = progress_data['data']['roomProgress']
else:
    progress_data = []

# Calculate the percentage of rooms completed
total_rooms = len(progress_data)
completed_rooms = sum(1 for room in progress_data if room['progressPercentage'] == 100)
in_progress_rooms = sum(1 for room in progress_data if 0 < room['progressPercentage'] < 100)
not_started_rooms = total_rooms - completed_rooms - in_progress_rooms

progress_data_sorted = sorted(progress_data, key=lambda x: x['progressPercentage'], reverse=True)

with open('progress_data_sorted.json', 'w') as f:
    json.dump(progress_data_sorted, f, indent=4)

labels = ['Completed', 'In Progress', 'Not Started']
sizes = [completed_rooms, in_progress_rooms, not_started_rooms]

if total_rooms == 0:
    print("No data to display in pie chart.")
else:
    colors = ['#4caf50', '#ffeb3b', '#f44336']
    explode = (0.1, 0, 0)

    plt.figure(figsize=(10, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    plt.title('Progress of TryHackMe Rooms')
    plt.axis('equal')

    plt.savefig('progress_pie_chart.png')

    plt.show()
