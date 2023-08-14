import sys
import multiprocessing
from create_url_qr import createUniqueUrl
from cam_recog_plate import run_cam
import requests
import time
from PIL import Image
from query_occup import update_occupancy

URL = 'https://spnswebapp.azurewebsites.net/'
sleep_time = 20
wifi_path = 'qr_imgs/home_wifi.jpg'
first_instruct_path = 'qr_imgs/instruct_wifi.jpg'
second_instruct_path = 'qr_imgs/instruct_app.jpg'

def main():
    print("start")

    cams_num = int(sys.argv[1])
    if cams_num>6 or cams_num<1:
        print("inserted unsupported number of cameras")
        exit(0)

    #initialize processes list
    processes = []

    #in any case need to enter entrance camera
    parking_entrance_cam = int(sys.argv[2])
    parking_entrance_queue = multiprocessing.Queue()
    parking_entrance_process = multiprocessing.Process(target=run_cam,args=(\
    parking_entrance_cam,parking_entrance_queue,))
    processes.append(parking_entrance_process)

    #get arguments, initialize queues and processes
    if cams_num>1:
        first_floor_entrance_cam = int(sys.argv[3])
        first_floor_entrance_queue = multiprocessing.Queue()
        first_floor_entrance_process = multiprocessing.Process(target=run_cam,args=(\
        first_floor_entrance_cam,first_floor_entrance_queue,))
        processes.append(first_floor_entrance_process)

    if cams_num>2:
        parking_exit_cam = int(sys.argv[3])
        parking_exit_queue = multiprocessing.Queue()
        parking_exit_process = multiprocessing.Process(target=run_cam,args=(\
        parking_exit_cam,parking_exit_queue,))
        processes.append(parking_exit_process)

    if cams_num>3:
        ground_floor_exit_cam = int(sys.argv[3])
        ground_floor_exit_queue = multiprocessing.Queue()
        ground_floor_exit_process = multiprocessing.Process(target=run_cam,args=(\
        ground_floor_exit_cam,ground_floor_exit_queue,))
        processes.append(ground_floor_exit_process)

    if cams_num>4:
        first_floor_exit_cam = int(sys.argv[3])
        first_floor_exit_queue = multiprocessing.Queue()
        first_floor_exit_process = multiprocessing.Process(target=run_cam,args=(\
        first_floor_exit_cam,first_floor_exit_queue,))
        processes.append(first_floor_exit_process)

    if cams_num>5:
        second_floor_entrance_cam = int(sys.argv[3])
        second_floor_entrance_queue = multiprocessing.Queue()
        second_floor_entrance_process = multiprocessing.Process(target=run_cam,args=(\
        second_floor_entrance_cam,second_floor_entrance_queue,))
        processes.append(second_floor_entrance_process)

    print("initialize queues")

    process_started = [False for i in range(cams_num)]

    #create occupancy query
    query_process = multiprocessing.Process(target=update_occupancy)
    query_process.start()

    while True:
        for index, process in enumerate(processes):
            print("examining process")
            if not process.is_alive() and not process_started[index]:
                process.start()
                process_started[index]=True

            if process.exitcode is not None and process.exitcode==0:
                print("process exited with 0")
                if index==0: #entrance_cam
                    #initialize location and web, open qr code
                    print("qr_process")
                    res = parking_entrance_queue.get()
                    print("the plate is: " +str(res))
                    url = "https://spnsfunctions.azurewebsites.net/api/InsertVehicleEntity?"
                    data = {"Floor": 0, "Section": "IN", "LicensePlate": res}
                    response = requests.post(url, data=data)
                    if response.status_code==200:
                        print("request was successful")
                    else:
                        print("request failed with status code: "+str(response.status_code))
                    #show wifi qr
                    #give instruction to scan wifi
                    img = Image.open(first_instruct_path)
                    img.show()
                    time.sleep(4)
                    #show wifi qr
                    img = Image.open(wifi_path)
                    img.show()
                    #short break to scn the code and connect to the network
                    time.sleep(10)
                    #give instruction to scan app qr
                    img = Image.open(second_instruct_path)
                    img.show()
                    time.sleep(4)
                    #show web qr
                    license_args = str("?licenseplate="+str(res))
                    img_path = createUniqueUrl(license_args)
                    img = Image.open(img_path)
                    img.show()
                    print("after showing qr")

                elif index==2:
                    #delete location
                    res = parking_exit_queue.get()
                    url = "https://spnsfunctions.azurewebsites.net/api/RemoveVehicleEntity?"
                    data = {"Floor": 2, "Section": "OUT", "LicensePlate": res}
                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        print("request was successful")
                    else:
                        print("request failed with status code: "+str(response.status_code))

                elif index==1:
                    #update location, index==1
                    res = first_floor_entrance_queue.get()
                    url = "https://spnsfunctions.azurewebsites.net/api/UpdateVehicleLocation?"
                    data = {"Floor": 1, "Section": "IN", "LicensePlate": res}
                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        print("request was successful")
                    else:
                        print("request failed with status code: "+str(response.status_code))

                elif index==3:
                    #update location, index==3
                    res = ground_floor_exit_queue.get()
                    url = "https://spnsfunctions.azurewebsites.net/api/UpdateVehicleLocation?"
                    data = {"Floor": 0, "Section": "OUT", "LicensePlate": res}
                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        print("request was successful")
                    else:
                        print("request failed with status code: "+str(response.status_code))

                elif index==4:
                    #update location, index==4
                    res = first_floor_exit_queue.get()
                    url = "https://spnsfunctions.azurewebsites.net/api/UpdateVehicleLocation?"
                    data = {"Floor": 1, "Section": "OUT", "LicensePlate": res}
                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        print("request was successful")
                    else:
                        print("request failed with status code: "+str(response.status_code))

                elif index==5:
                    #update location, index==1
                    res = second_floor_entrance_queue.get()
                    url = "https://spnsfunctions.azurewebsites.net/api/UpdateVehicleLocation?"
                    data = {"Floor": 2, "Section": "IN", "LicensePlate": res}
                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        print("request was successful")
                    else:
                        print("request failed with status code: "+str(response.status_code))


                time.sleep(sleep_time)
                process.terminate()
                #start a new process and replace the old one
                if index==0:
                    new_process = multiprocessing.Process(target=run_cam, args = (\
                    parking_entrance_cam,parking_entrance_queue,))
                elif index==1:
                    new_process = multiprocessing.Process(target=run_cam, args = (\
                    first_floor_entrance_cam,first_floor_entrance_queue,))
                elif index==2: #index==2
                    new_process = multiprocessing.Process(target=run_cam, args = (\
                    parking_exit_cam,parking_exit_queue,))
                elif index==3:
                    new_process = multiprocessing.Process(target=run_cam, args = (\
                    ground_floor_exit_cam,ground_floor_exit_queue,))
                elif index==4:
                    new_process = multiprocessing.Process(target=run_cam, args = (\
                    first_floor_exit_cam,first_floor_exit_queue,))
                elif index==5:
                    new_process = multiprocessing.Process(target=run_cam, args = (\
                    second_floor_entrance_cam,second_floor_entrance_queue,))


                processes[index] = new_process
                new_process.start()
                print("on our way to reinitialize the process")

        time.sleep(1)

if __name__=="__main__":
    main()
