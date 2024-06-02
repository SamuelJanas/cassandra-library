import requests
import json

# Define the URL of the server
base_url = "http://localhost:8888/remove_reservation"

# Function to remove all reservations
def remove_all_reservations():
    # Assuming reservations are fetched from another endpoint
    reservations_url = "http://localhost:8888/api/reservations"
    reservations = requests.get(reservations_url).json()
    counter = 0
    total_reservations = len(reservations)
    # Iterate through reservations and send POST request to remove each one
    for reservation in reservations:
        payload = {"book_id": reservation["book_id"], "user_id": reservation["user_id"]}
        requests.post(base_url, data=json.dumps(payload))
        counter += 1
        if counter % 250 == 0:
            total_reservations -= 250
            print(f"{total_reservations} reservations remaining")
            counter = 0

# Call the function to remove all reservations
remove_all_reservations()
