import requests

url = 'https://spnsfunctions.azurewebsites.net/api/UpdateVehicleLocation?'
data1 = {'LicensePlate': '12345678', 'Section': 'IN', 'Floor': 1}
data2 = {'LicensePlate': '99999999', 'Section': 'OUT', 'Floor': 1}
data3 = {'LicensePlate': '83457962', 'Section': 'IN', 'Floor': 2}
data4 = {'LicensePlate': '75062834', 'Section': 'OUT', 'Floor': 0}

data = data1

response = requests.post(url, data=data)
print(response.text)