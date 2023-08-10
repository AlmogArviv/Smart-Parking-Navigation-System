import requests

url = 'https://spnsfunctions.azurewebsites.net/api/RemoveVehicleEntity?'
data1 = {'LicensePlate': '12345678', 'Section': 'OUT', 'Floor': 2}
data2 = {'LicensePlate': '99999999', 'Section': 'OUT', 'Floor': 2}
data3 = {'LicensePlate': '83457962', 'Section': 'OUT', 'Floor': 2}
data4 = {'LicensePlate': '75062834', 'Section': 'OUT', 'Floor': 2}

data = data1

response = requests.post(url, data=data)
print(response.text)