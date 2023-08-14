import qrcode

URL = 'https://spnswebapp.azurewebsites.net/'

def createUniqueUrl(driverLicensePlate):
    img = qrcode.make(URL+driverLicensePlate)


    # if needed we can save the image on the system and open it in a different way
    path = '/home/guy/qr_test_code_01.png'
    with open('/home/guy/qr_test_code_01.png', 'wb') as f:
        img.save(f)

    return path