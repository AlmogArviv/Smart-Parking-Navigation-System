IOT Project
Smart Parking Navigation System
by
Almog Arviv and Guy Paz Ben Itzhak

Introduction
This project is a POC for a smart parking navigation system targeted at closed, primarily underground, parking lots where visibility is limited, orientation is challenging and parking spaces are scarce.
We aim to enhance the ability to navigate through a closed off, GSP disabled parking lot environments by using an array of cameras to create a system that maps a driver’s position by using AI and ML to capture license plate numbers and send new locations updates through azure services, directly to a web application in the user’s smartphone.

System Overview
The smart parking system consists of these key components:
IOT Module
Camera sensors positioned strategically within the parking lot to capture license plate information and monitor vehicle location.
Entrance camera at front gates, Exit cameras at Exit points and optional entry and exit point locations for update cameras throughout the parking lot sections.
WiFi and a unique QR code is rendered at the front gates for every vehicle.
Occupancy, azure database communication and updates are sent by the device.
Azure Web Application
Pre rendered customized map of the parking lot on the navigation screen.
Menu actions for automatic and custom navigation, updates and information, save location options.
Auxiliary apps options for outdoor vehicle navigation, payment solutions.

Flow - Initialization:
Parking lot map is created using the blueprints of the structure.
Development team is assigned with integrating IOT devices and cameras throughout the parking lot, while maintaining data of each capture point as coordinates for the map.
Entry, exit, update points are assigned and other specific instances of the parking lot are mapped.
A web application is created on Azure Platform that will run on Azure’s services.
Authorization for administrative actions and data accessibility are assigned to the parking lot personal.

Flow - Communication:
Camera picks up a license plate at one of the entry point (entry, exit, section ).
The IOT device uses the number captured to create a QR for that number while Azure creates a unique URL that this QR code will be directed to.
The IOT device then renders the QR code on the entry point device’s screen.
The driver will use his smartphone’s camera to capture the QR code and enter the web application.
Everytime the driver runs into a camera inside the parking lot the camera will capture the number plate and the iot device will activate a function on Azure according to the camera’s role.
Azure will update its tables and will send a SignalR to the necessary URL addresses that has this drivers plate number.
The map in the web application will update according to the new SignalR message.
When the driver exits the parking lot through one of the exit points, the IOT device will send a removal function call to Azure which will update its tables and remove this vehicle from them as well. 

IOT Device
The IOT device is a Raspberry Pi that is attached to several cameras.
In order to detect the license plate number, we have written a code that uses an OCR (Optical Character Recognition) tool  called Tesseract. The code reduces noise in the image and converts it to grayscale. It then performs edge detection, finds contours and looks for contours that have 4 corners. It then uses Tesseract to detect the number.
The IOT device runs a Python program which initiates the cameras and runs  in parallel the license plate detection algorithm for each frame received by the cameras. It then sends an appropriate http request to Azure Functions. For the entrance camera, the IOT device also presents a QR code enabling the user to connect to the application. Another http request is sent every minute to query the occupancy. 

Azure
Azure services that were used in the project for communication, storage and web application deployment:
Web app: web application deployment.
Functions: interaction between the Web app, IOT devices and the user.
Storage: web application sources, database.
SignalR: broadcast update messages.

Azure Web Application
Map: 
we chose to use Leaflet, an open source interactive map javascript library for our map functionality.
Menu:
Find a space: use occupancy data to navigate to most likely section to find a parking space. Alternatively, user can request specific location for navigation.
Navigate to exit: navigate to closest exit point.
Save location: option to input your parking spot location that will be saved on the device browser's cookies.
Change vehicle number: user ability to manually correct false number detection. it is possible to change the vehicle number on the app so that other update cameras will still send updates to the user map.
Auxiliary navigation and payment applications options: Google Maps, Waze, Pango.

Azure Functions
Insert - inserts a new unique entity of a vehicle number to the Azure occupancy table.
Remove - removes the entity of the vehicle from the tables.
Update - updates the Azure table and sends a SignalR location update to the user’s URL.
Query Occupancy - queries the Azure table for occupancy data by section and sends a SignalR message with the update for all users.

Improvements / Bugs / WIP
IOT Device cameras algorithm improvements:
Continuous scanning on all cameras, front gate interval times optimization.
Navigation:
Directions for the navigation on the map proved to be difficult to integrate using leaflet, for future iterations a different plugin should be considered.
Admin user page:
Monitor tables data and IOT.Using the information from Azure hub proved to be sufficient for admin information, a standalone web application is possible but might be redundant.
Function triggers:
While the groundwork for IOT devices is present in the project, Http triggers were used throughout the project to control communication between the IOT device and the web application. 
Using Azure IOT Hub and devices, while controlling the functionality through IOT triggers proved to be difficult using a virtual machine to simulate the usage of a Raspberry Pi 4. 
