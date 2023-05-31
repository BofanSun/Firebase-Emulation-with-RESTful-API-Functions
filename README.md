# Firebase-Emulation-with-RESTful-API-Functions

## Description
This project aims to emulate a database resembling the Google Firebase with complete RESTful API functions, including get (request data from database and print it out), put (write a given value), post (upload new values), patch (update existing values), and delete (remove existing values). For the data set, we chose the World Bird Master List version 13.1 published by the International Ornithological Committee (IOC) to generate a database recording the Latin names of all Orders and Families of birds, as well as their English common name and number of Genus under each Family. 

## Requirements
1. flask
2. flask_socketio 
3. pymongo
4. asyncio 
5. websockets 
6. logging
7. json 

To install the above packages, use the following command: pip install -r requirements.txt
'requirements.txt' file has a list of all the necessary packages required to run this code. 

## Data Sources
1. IOC World Bird List v13.1
(URL: https://www.worldbirdnames.org/new/ioc-lists/master-list-2/)
Explanation: world bird master list by IOC recording more than 11,000 bird species around the world. Here we used the XML file from the website.

## Running the Code
'main.py': it uses 'xml_to_json.py' and 'json_to_mongoDB.py', the output will be two JSON file and one will be used to upload into MongoDB. Our 'main.py' can be run by typing command python3 main.py [file name] in the path of the file. Run this first before running anything else! For example: 
'''
python3 main.py master_ioc-names_xml.xml 
'''

'server.py': To run the code, type in the command python3 server.py in the path of the file. After running the script, the user could then input the curl command in the local terminal to commence the query in local MongoDB. See 'command.txt' file for examples. The result and error message will be printed in local terminal. 

'websocket-server.py': To run the code, type in the command python3 websocket-server.py in the path of the file. After running the script, the user could then use the webapp.html file to commence querying the local MongoDB database via the html GUI. The result and error message will be printed in both local terminal and html GUI. 

'webapp.html': To run the Webapp GUI, open this file in any browser. Make sure to put the 'red_bird.png' and 'red_bird2.png' in the same path with this file. 
