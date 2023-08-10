import requests

url = 'https://spnsfunctions.azurewebsites.net/api/QueryOccupancy?'

response = requests.post(url)
print(response.text)