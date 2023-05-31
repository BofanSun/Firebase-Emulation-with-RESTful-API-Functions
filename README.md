# Firebase-Emulation-with-RESTful-API-Functions

## Description
This project aims to first emulate a Flask server resembling the Google Firebase with complete RESTful API functions that support curl command-line interactions, including GET (request data from database and print it out), PUT (write a given value), post (upload new values), PATCH (update existing values), and DELETE (remove existing values). And second goal of this project is to develop a Web app which CRUD functions were embedded and demonstrates real-time update and syncing of the dataset with the server via WebSocket.

For the dataset, the World Bird Master List version 13.1 published by the International Ornithological Committee (IOC) was chosen to generate a database recording the Latin names of all Orders and Families of birds, as well as their English common name and number of Genus under each Family. 

![WechatIMG742](https://github.com/BofanSun/Firebase-Emulation-with-RESTful-API-Functions/assets/93634338/856094e9-c7fd-4b47-a471-11370924aaf6)

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
IOC World Bird List v13.1
(URL: https://www.worldbirdnames.org/new/ioc-lists/master-list-2/)
Explanation: world bird master list by IOC recording more than 11,000 bird species around the world. Here we used the XML file from the website.

## Running the Code
'main.py': it uses 'xml_to_json.py' and 'json_to_mongoDB.py', the output will be two JSON file and one will be used to upload into MongoDB. Our 'main.py' can be run by typing command python3 main.py [file name] in the path of the file. Run this first before running anything else! For example: 
```python
python3 main.py master_ioc-names_xml.xml 
```

'server.py': To run the code, type in the following command in the path of the file. After running the script, the user could then input the curl command in the local terminal to commence the query in local MongoDB. See 'command.txt' file for examples. The result and error message will be printed in local terminal. 
```python
python3 server.py
```

'websocket-server.py': To run the code, type in the following command in the path of the file. After running the script, the user could then use the webapp.html file to commence querying the local MongoDB database via the html GUI. The result and error message will be printed in both local terminal and html GUI. 
```python
python3 websocket-server.py
```

'webapp.html': To run the Webapp GUI, open this file in any browser. Make sure to put the 'red_bird.png' and 'red_bird2.png' in the same path with this file. 
