# IOT Project - A Smart Parking Navigation System - Almog Arviv and Guy Paz Ben Itzhak

## Introduction
This project is a POC for a smart parking navigation system targeted at closed, primarily underground, parking lots where visibility is limited, orientation is challenging and parking spaces are scarce.
We aim to enhance the ability to navigate through a closed off, GSP disabled parking lot environments by using an array of cameras to create a system that maps a driver’s position by using AI and ML to capture license plate numbers and send new locations updates through Azure services, directly to a web application in the user’s smartphone.

## How to use


## System Overview
The smart parking system consists of these 2 key components:

### IOT Module
Includes Camera sensors positioned strategically within the parking lot to capture license plate information and monitor vehicle location.
Entrance camera at are positioned at the front gates, Exit cameras at the Exit points and optional entry and exit point locations for update cameras are located throughout the parking lot sections.
WiFi and a unique QR code are rendered at the front gates for every vehicle.
Occupancy data, Azure database communication and updates are sent by the device.

### Azure Web Application
It includes a pre-rendered customized map of the parking lot on the navigation screen.
There are menu actions for automatic and custom navigation, updates and information, save location options.
In addition, auxiliary apps options are provided for outdoor vehicle navigation and payment solutions.

## Flow - Initialization:
A parking lot map is created using the blueprints of the structure.
A development team is assigned with integrating IOT devices and cameras throughout the parking lot, while maintaining data of each capture point as coordinates for the map.
Entry, Exit, abd Update points are assigned and other specific instances of the parking lot are mapped.
A web application is created on the Azure Platform that will run on Azure’s services.
Authorization for administrative actions and data accessibility are assigned to the parking lot personal.

## Flow - Communication:
The camera picks up a license plate at one of the entry points (entry, exit, section ).
The IOT device uses the number captured to create a QR for that number while Azure creates a unique URL that this QR code will be directed to.
The IOT device then renders the QR code on the entry point device’s screen.
The driver will use the smartphone’s camera to capture the QR code and enter the web application.
Everytime the driver runs into a camera inside the parking lot the camera will capture the number plate and the IOT device will activate a function on Azure according to the camera’s role.
Azure will update its tables and will send a SignalR to the necessary URL addresses that has this driver's plate number.
The map in the web application will update according to the new SignalR message.
When the driver exits the parking lot through one of the exit points, the IOT device will send a removal function call to Azure which will update its tables and remove this vehicle from them as well. 

## IOT Device
The IOT device is a Raspberry Pi that is attached to several cameras.
In order to detect the license plate number, we have written a code that uses an OCR (Optical Character Recognition) tool called Tesseract. The code reduces noise in the image and converts it to grayscale. It then performs edge detection, finds contours and looks for contours that have 4 corners. It then uses Tesseract to detect the number.
The IOT device runs a Python program which initiates the cameras and runs in parallel the license plate detection algorithm for each frame received by the cameras. It then sends an appropriate http request to Azure Functions. For the entrance camera, the IOT device also presents a QR code enabling the user to connect to the application and a WiFi connection option. Another http request is sent every minute to Azure to query the occupancy, independent of the parallel cameras requests. 

## Azure
Azure services that were used in the project for communication, storage and web application deployment are:
  **Web app**: web application deployment.
  **Functions**: interaction between the Web app, IOT devices and the user.
  **Storage**: web application sources, database.
  **SignalR**: broadcast update messages.

## Azure Web Application
Map: 
we chose to use Leaflet, an open source interactive map Javascript library for our map functionality.
Menu:
Find a space: use occupancy data to navigate to most likely section to find a parking space. Alternatively, user can request specific location for navigation.
Navigate to exit: navigate to closest exit point.
Save location: option to input your parking spot location that will be saved on the device browser's cookies.
Change vehicle number: user ability to manually correct false number detection. it is possible to change the vehicle number on the app so that other update cameras will still send updates to the user map.
Auxiliary navigation and payment applications options: Google Maps, Waze, Pango.

## Azure Functions
Insert - inserts a new unique entity of a vehicle number to the Azure occupancy table.
Remove - removes the entity of the vehicle from the tables.
Update - updates the Azure table and sends a SignalR location update to the user’s URL.
Query Occupancy - queries the Azure table for occupancy data by section and sends a SignalR message with the update for all users.

## Improvements / Bugs / WIP
IOT Device cameras algorithm improvements:
Continuous scanning on all cameras, front gate interval times optimization.
Navigation:
Directions for the navigation on the map proved to be difficult to integrate using Leaflet, for future iterations a different plugin should be considered.
Admin user page:
Monitor tables data and IOT. Using the information from Azure hub proved to be sufficient for admin information, a standalone web application is possible but might be redundant.
Function triggers:
While the groundwork for IOT devices is present in the project, Http triggers were used throughout the project to control communication between the IOT device and the web application. 
Using Azure IOT Hub and devices, while controlling the functionality through IOT triggers proved to be difficult using a virtual machine to simulate the usage of a Raspberry Pi 4. 
