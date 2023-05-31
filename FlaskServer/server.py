from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient, ASCENDING

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['dsci551']
collection = db['project']

# GET request to get specific information from database
@app.route('/')
@app.route('/project', methods=['GET'])
def get_collection_data():
    try:
        if len(request.args) == 0:
            result = list(collection.find())
            # convert ObjectId to string for serialization
            for d in result:
                d['_id'] = str(d['_id'])
            return(jsonify(result))
        else:
            data = []
            order_by = request.args.get('orderBy')
            equal_to = request.args.get('equalTo')
            start_at = request.args.get('startAt')
            end_at = request.args.get('endAt')
            limit_to_first = request.args.get('limitToFirst')
            limit_to_last = request.args.get('limitToLast')
            
            #error handling when no orderby is provided
            if order_by == None:
                return jsonify({'Error':'orderBy must be defined.'})
            else:
                # Apply filtering conditions
                if order_by == "$key":
                    order_by = "_id"
                    pipline = [{'$sort':{"_id":1}}]
                    results = collection.aggregate(pipline)
                elif order_by == "$value":
                    order_by = "value"
                    pipline = [{'$sort':{"value":1}}]
                    results = collection.aggregate(pipline)
                else:
                    if order_by != "order_name":
                        collection.create_index(order_by)
                        pipline = [{'$sort':{order_by:1}}]
                        results = collection.aggregate(pipline)
                    else:
                        pipline = [{'$sort':{order_by:1}}]
                        results = collection.aggregate(pipline)
                        
                if start_at != None:
                    if start_at.isdigit():
                        start_at = int(start_at)
                    pipline.append({'$match':{order_by:{'$gte':start_at}}})
                    results = collection.aggregate(pipline)
                             
                if end_at != None:
                    if end_at.isdigit():
                        end_at = int(end_at)
                    pipline.append({'$match':{order_by:{'$lte':end_at}}})
                    results = collection.aggregate(pipline) 
                
                if equal_to != None:
                    if equal_to.isdigit():
                        equal_to = int(equal_to)
                    pipline.append({'$match': {order_by: equal_to}})
                    results = collection.aggregate(pipline)
                
                #Error handling where user enters limitToFirst and limitToLast together
                if limit_to_first != None and limit_to_last != None:
                    return jsonify({'Error':'Cannot implement limitToFirst and limitToLast together.'})
                else:
                    if limit_to_first != None:
                        if limit_to_first.isdigit():
                            limit_to_first = int(limit_to_first)
                        else:
                            return jsonify({'Error':'limitToFirst have to be a number.'})
                        if limit_to_first <= 0:
                            return jsonify({'Error':'limitToFirst must be a positive number.'})
                        pipline.append({'$limit':limit_to_first})
                        results = collection.aggregate(pipline)
                    
                    if limit_to_last != None:
                        if limit_to_last.isdigit():
                            limit_to_last = int(limit_to_last)
                        else:
                            return jsonify({'Error':'limitToLast have to be a number.'})
                        if limit_to_last <= 0:
                                return jsonify({'Error':'limitToLast must be a positive number.'})
                        count = 0 #number of existing records
                        for doc in results:
                            count += 1
                        skip = count - limit_to_last
                        pipline.append({'$skip':skip})
                        results = collection.aggregate(pipline)
                        
            for result in results:
                result['_id'] = str(result['_id'])
                data.append(result)
            return jsonify(data), 200    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT request to write value to a given record
@app.route('/project/<order_name>', methods=['PUT'])
def put(order_name):
    try:
        if collection.find_one({"order_name":order_name}) == None:
            return jsonify({'Error': 'Record not found.'}), 404
        else:
            data = request.json
            data["order_name"] = order_name
            result = collection.replace_one({'order_name': order_name}, data)
            if result.modified_count > 0:
                updated = collection.find_one({'order_name': order_name})
                updated["_id"] = str(updated["_id"])
                return jsonify({'UPDATED RECORD': updated}), 200
            else:
                return jsonify({'Error': 'Record updat not successful.'}), 404       
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST request to create a new record
@app.route('/project', methods=['POST'])
def create_data():
    data = request.json
    try:
        data["order_name"]
        #check whether the provided order name already exists, if not, insert data
        if collection.find_one({"order_name":data["order_name"]}) != None:
            return jsonify({'Error': 'Duplicate order Name, record is not inserted.'})
        else:
            result = collection.insert_one(data)
            data['_id'] = str(result.inserted_id)
            inserted = collection.find_one({"_id":result.inserted_id})
            inserted["_id"] = str(inserted["_id"])
            if result.inserted_id:
                return jsonify({'Inserted Record': inserted}), 200
            else:
                return jsonify({'Error': 'Record not inserted.'}), 500
    except KeyError:    
        return jsonify({'Error': 'No order name provided.'}), 404

# PATCH request to update data partially
@app.route('/project/<order_name>', methods=['PATCH'])
def partial_update(order_name):
    try:
        if collection.find_one({"order_name":order_name}) == None:
            return jsonify({'Error': 'Record not found'}), 404
        else:
            data = request.json
            collection.update_one({'order_name': order_name}, {'$set': data})
            updated = collection.find_one({'order_name': order_name})
            updated["_id"] = str(updated["_id"])
            return jsonify({'UPDATED RECORD': updated}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE request to delete a record
@app.route('/project/<order_name>', methods=['DELETE'])
def delete_data(order_name):
    try:
        if collection.find_one({"order_name":order_name}) == None:
            return jsonify({'Error': 'Record not found'}), 404
        else:
            result = collection.delete_one({'order_name': order_name})
            if result.deleted_count == 1:
                return jsonify({'message': 'Record deleted successfully'})
            else:
                return jsonify({'Error': 'Record was not delete successfull'}), 404
    except Exception as e:
        return jsonify({'Error': str(e)}), 400

app.run(debug=True)
