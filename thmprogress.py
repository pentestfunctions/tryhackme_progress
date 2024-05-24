import requests
import matplotlib.pyplot as plt
import json

cookie = "RANDOM_SID"

# Function to fetch free rooms from the API
def fetch_free_rooms(exclude_windows):
    base_url = "https://tryhackme.com/api/v2/hacktivities/extended-search"
    params = {
        "kind": "all",
        "difficulty": "all",
        "order": "relevance",
        "roomType": "all",
        "contentSubType": "free",
        "limit": 100
    }

    free_rooms = []

    # Iterate through pages 1 to 20
    for page in range(1, 11):
        params["page"] = page
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'docs' in data['data']:
                for room in data['data']['docs']:
                    if exclude_windows:
                        if not any(tag['label'].lower() == 'windows' for tag in room['tagDocs']):
                            free_rooms.append(room)
                    else:
                        free_rooms.append(room)
        else:
            print(f"Failed to fetch data for page {page}: {response.status_code}")
    
    return free_rooms

# Function to fetch progress data for the given room codes
def fetch_progress_data(room_codes, cookie):
    room_codes_str = "%2C".join(room_codes)
    url = f"https://tryhackme.com/api/v2/hacktivities/search-progress?roomCodes={room_codes_str}"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "priority": "u=1, i",
    }
    cookies = {
        "connect.sid": cookie,
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch progress data: {response.status_code}")
        return {}

# Main script execution
exclude_windows = False  # Change this to False to include rooms with Windows rating
free_rooms = fetch_free_rooms(exclude_windows)

room_codes = [room['code'] for room in free_rooms]

progress_data = fetch_progress_data(room_codes, cookie)

if 'data' in progress_data and 'roomProgress' in progress_data['data']:
    progress_data = progress_data['data']['roomProgress']
else:
    progress_data = []

total_rooms = len(progress_data)
completed_rooms = sum(1 for room in progress_data if room['progressPercentage'] == 100)
in_progress_rooms = sum(1 for room in progress_data if 0 < room['progressPercentage'] < 100)
not_started_rooms = total_rooms - completed_rooms - in_progress_rooms

labels = ['Completed', 'In Progress', 'Not Started']
sizes = [completed_rooms, in_progress_rooms, not_started_rooms]

# Chart title
chart_title = 'Completion Rate of TryHackMe Free Rooms (Excluding Windows)' if exclude_windows else 'Completion Rate of TryHackMe Free Rooms'

# Check if all sizes are zero
if total_rooms == 0:
    print("No data to display in pie chart.")
else:
    colors = ['#4caf50', '#ffeb3b', '#f44336']
    explode = (0.1, 0, 0)  # explode the 1st slice (Completed)

    # Plot the pie chart
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    plt.title(chart_title)
    plt.axis('equal')

    # Save the plot as an image file
    plt.savefig('completion_rate_pie_chart.png')

    # Show the plot
    plt.show()

# Save the sorted progress data to a JSON file
with open('progress_data_sorted.json', 'w') as f:
    json.dump(progress_data, f, indent=4)
