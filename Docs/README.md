### A Raspberry Pi Project to automated a Cat Door using cat face recognition (Python)



###### Hardware:

* Raspberry Pi 4 with 8GB RAM
* Through beam IR Sensor
* H-Bridge
* 12V Linear actuator with power supply
* RaspberryPI Expansion board Power Relay Module
* Micro limit switches (momentary)
* Infrared Photoelectric Switch
* Arducam 1080P low light USB camera



###### I/O Mapping

| Channel | Description        | Comment                      | Config  |

| ---     | ---                | ---                          | ---     |

| 4       | Proximity Switch   | initiate face recognition    | Input   |

| 27      | Door Open LS       | N.O. contact for opened door | Input   |

| 22      | Door Closed LS     | N.O. contact for door closed | Input   |

| 5       | Manual door open   | Momentary button to open door| Input   |

| 6       | Manual door close  | Momentary button to open door| Input   |

| 26      | Door Open (motor)  | Command Door Open            | Output  |

| 20      | Door Close (motor) | Command Door Open            | Output  |

| 23      | Safety Switch      | Through Beam Sensor          | Input   |





###### Software

The software uses pretrained models to extract cat faces from photographs and to recognize landmarks (detector.svm and predictor.dat). This work was performed here: *https://github.com/marando/pycatfd?tab=readme-ov-file#readme*.



A binary classifier was trained to differentiate one specific cat from other cats. This is included in models/svc\_model.pkl. Software to create the binary classifier will be delivered to a separate repository.



###### High level functionality:

* The proximity switch is mounted to sense an object that approaches the cat door.
* When an object is sensed, the USB camera takes 5 photos of the object in front of the cat door.
* The models above are used to attempt to extract a cat face, determine landmarks and determine if the object is indeed the desired cat.
* Whenever the process is triggered, an email is sent to a configurable email address with the photos and results.
* If the cat is recognized, the linear actuator opens the door for a configurable period of time. Note that configuration allows override of this feature. A through beam sensor will stop the door from closing and reinitiate opening if triggered.



###### Implementation: 

The code is separated into projects: 

* state\_machine: The business logic resides in a series of state machine classes state machine. Each state is represented by a class that inherits from a base class.
* ML: Utilizes the detector and predictor to extract a cat face and landmarks from the photographs taken. Contains the code for the binary classifier. Returns whether or not the current set of photos recognizes the cat that the binary classifier is trained for. 
* IO: Abstracts the specifics of RaspberryPi from the business logic. Imports RPi.GPIO to configure and communicate with the RaspberryPI IO. Presents methods to the state machine for getting and setting IO.
* email\_comm: A class to send email message and photos to a configurable email address. This implementation assumes gmail and  most of the required information for email is stored in configuration data. However, for security purposes, the GMAIL application password is saved as an environment variable.  
* camera: Controls the USB camera. 
* Util: contains the configuration manager. User configurable items are held in a json file. The ConfigUtility class reads the json file, holds as a dictionary and exposes a method to allow other classes to retrieve configuration values.   
* main.py: initiates and configures the logger. Retrieves a dictionary of state names (k) and individual state instances (v). The code uses this dictionary to progress the state machine based  the state machine business logic. The script loops indefinately, sleeping for .1 seconds on each iteration.



###### Requirements: 

The "Docs" folder of this project has an export of the python libraries needed (requirements.txt).









 



 

