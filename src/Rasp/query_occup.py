import time
import requests

def update_occupancy():
    url = "https://spnsfunctions.azurewebsites.net/api/QueryOccupancy?"
    while True:
        response = requests.post(url)
        if response.status_code == 200:
            print("Occupancy query request was successful")
        else:
            print("Occupancy query request failed with status code: "+str(response.status_code))
        time.sleep(60)