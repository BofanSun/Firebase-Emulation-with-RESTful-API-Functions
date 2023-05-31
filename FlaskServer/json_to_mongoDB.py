import json
from pymongo import MongoClient

def jsonmongo():   
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dsci551']
    collection = db['project']

    #store JSON data into MongoDB
    with open("order_family.json", "r") as f:
        data = json.load(f)
        result = collection.insert_many(data)
    collection.create_index('order_name', unique=True)

    if result.acknowledged:
        print("Insertion successful!")
    else:
        print("Insertion failed.")
    client.close()