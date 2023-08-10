import requests

url = 'https://spnsfunctions.azurewebsites.net/api/InsertVehicleEntity?'
data1 = {'LicensePlate': '12345678', 'Section': 'IN', 'Floor': 0}
data2 = {'LicensePlate': '99999999', 'Section': 'IN', 'Floor': 0}
data3 = {'LicensePlate': '83457962', 'Section': 'IN', 'Floor': 0}
data4 = {'LicensePlate': '75062834', 'Section': 'IN', 'Floor': 0}

data = data1

response = requests.post(url, data=data)
print(response.text)