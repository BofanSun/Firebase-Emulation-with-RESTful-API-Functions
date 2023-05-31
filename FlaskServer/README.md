# Description

First part of Flask Server is data cleaning. The original dataset in XML format was converted into Python dictionary, 
and writed into JSON format. The final data set contains the Orders’ scientific names in Latin, code, and note; 
the Families under each Order are recorded under the Order node, information including scientific name, English common name, 
and number of Genus under each Family are presented. 

The dataset was then uploaded into the MongoDB database. The key to access the MongoDB was created through the default server port localhost: 27017. 
In this step, each node (Order) would be offered with a unique id (_id). In addition, since we assume order name is unique, 
we provided each “order_name” a unique index to avoid duplication.

Then a Flask-based RESTful server was developed to handle CRUD requests sent from curl commands and established communication between the server and MongoDB 
database, command-line interactions and operations was enabled for data retrieval, updating, creation, and deletion.

## Running the Code
'main.py': it uses 'xml_to_json.py' and 'json_to_mongoDB.py', the output will be two JSON file and one will be used to upload into MongoDB. Our 'main.py' can be run by typing command python3 main.py [file name] in the path of the file. Run this first before running anything else! For example: 
```python
python3 main.py master_ioc-names_xml.xml 
```

'server.py': To run the code, type in the following command in the path of the file. After running the script, the user could then input the curl command in the local terminal to commence the query in local MongoDB. 
```python
python3 server.py
```
