# more details at: https://websockets.readthedocs.io/en/6.0/intro.html
# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import logging
import json
from pymongo import MongoClient
import pymongo
from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
from time import sleep as tsleep

# values for all
STATE = {'msg': ''}
USERS = set()
print('start!')

# mongoDB? 
client = MongoClient('mongodb://localhost:27017/')
db = client['dsci551']
collection = db['project']

# test function for time
async def time(websocket, path):
    print("new connection path " + path)
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        #print(now)
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)

def state_event():
    return json.dumps({'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})

async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_users():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

def process_in(data_in): 
    temp = json.loads(data_in)
    temp_lst = []
    for i in temp: 
        if temp[i] == '': 
            temp_lst.append(i)
    for i in temp_lst: 
        del temp[i]
    data_out = json.dumps(temp)
    return data_out


# when get command from webapp 
async def receive_from_html(websocket, path): 
    # await websocket.send(state_event())
    async for message in websocket: 
        data = json.loads(message)
        # differentiate wtf was sent by client here!

        if data['action'] == 'request': 
        # 1 GET command. if empty input, return everything in collection 
        # sort, orderBy, equal, startat, endat, limittofirst, limittolast 
        # orderby plus everything else, or nothing at all! 
            # process_in()

            if data['orderBy'] == "" and data['equalTo'] == "" and data['startAt'] == "" and data['endAt'] == "" and data['limitToFirst'] == "" and data['limitToLast'] == "": 
                print('No query options entered! ')
                await websocket.send(str(list(collection.find())))

            query_dic = {}
            if data['orderBy'] != "": 
                query_dic['orderBy'] = data['orderBy']
            if data['equalTo'] != "": 
                query_dic['equalTo'] = data['equalTo']
            if data['startAt'] != "": 
                query_dic['startAt'] = data['startAt']
            if data['endAt'] != "": 
                query_dic['endAt'] = data['endAt']
            if data['limitToFirst'] != "": 
                query_dic['limitToFirst'] = data['limitToFirst']
            if data['limitToLast'] != "": 
                query_dic['limitToLast'] = data['limitToLast']

            # change all default values if exist in query dic
            #error handling when no orderby is provided
            if 'orderBy' not in query_dic: 
                order_by = None
                results = list(collection.find())
                await websocket.send(str(results))
            else: 
                order_by = query_dic['orderBy']
                if 'equalTo' in query_dic: 
                    equal_to = query_dic['equalTo']
                else: 
                    equal_to = None 
                if 'startAt' in query_dic: 
                    start_at = query_dic['startAt']
                else: 
                    start_at = None 
                if 'endAt' in query_dic: 
                    end_at = query_dic['endAt']
                else: 
                    end_at = None 
                if 'limitToFirst' in query_dic: 
                    limit_to_first = query_dic['limitToFirst']
                else: 
                    limit_to_first = None
                if 'limitToLast' in query_dic: 
                    limit_to_last = query_dic['limitToLast']
                else: 
                    limit_to_last = None 

                data2 = []
                if 'orderBy' not in query_dic:
                    await websocket.send('Error: orderBy must be defined.') 
                    print('Error: orderBy must be defined.')
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
                    if (limit_to_first != None) and (limit_to_last != None):
                        await websocket.send('Error: Cannot implement limitToFirst and limitToLast together.')
                        print('Error: Cannot implement limitToFirst and limitToLast together.')
                        results = []
                        #break
                    else: 
                        # print(type(limit_to_first),type(limit_to_last))
                        if limit_to_first != None:
                            try:       
                                if limit_to_first.isdigit():
                                    limit_to_first = int(limit_to_first)
                                else:
                                    await websocket.send('Error: limitToFirst have to be a number.')
                                    print('Error: limitToFirst have to be a number.')
                                    results=[]
                                if limit_to_first > 0:
                                    pipline.append({'$limit':limit_to_first})
                                    results = collection.aggregate(pipline)
                                else:
                                    await websocket.send('Error: limitToFirst must be a positive number.')
                                    print('Error: limitToFirst must be a positive number.')
                                    results=[]
                            except TypeError:
                                results=[]
                                await websocket.send('Error: limitToFirst must be a positive number.')
                                print('Error: limitToFirst must be a positive number.')
                                   
                        
                        if limit_to_last != None:
                            try:
                                if limit_to_last.isdigit():
                                    limit_to_last = int(limit_to_last)
                                else:
                                    await websocket.send('Error: limitToLast have to be a number.')
                                    print('Error: limitToLast have to be a number.')
                                    results=[]
                                if limit_to_last > 0:
                                    count = 0 #number of existing records
                                    for doc in results:
                                        count += 1
                                    skip = count - int(limit_to_last)
                                    pipline.append({'$skip':skip})
                                    results = collection.aggregate(pipline)
                                else:
                                    await websocket.send('Error: limitToLast must be a positive number.')
                                    print('Error: limitToLast must be a positive number.')
                                    results=[]
                            except TypeError:
                                results=[]
                                await websocket.send('Error: limitToLast must be a positive number.')       
                                print('Error: limitToLast must be a positive number.')                     
                                 
                try:
                    #only print out when results is not empty            
                    if results._has_next or len(result)!=0:                
                        for result in results:
                            result['_id'] = str(result['_id'])
                            ordern = str(result.get('order_name'))
                            code = str(result.get('code'))
                            note = str(result.get('note'))
                            family = str(result.get('family'))
                            answer = "This type of Bird's ID is: " + result['_id'] + ', Order name is: ' + ordern + ', code is: ' + code + ', Note is: ' + note + ', family information as: ' + family + '\n'
                            data2.append(answer)
                            data2.append('\n')
                        await websocket.send(data2)
                        print(data2)
                    print('Get successful! ')
                except (TypeError, AttributeError) as error:
                    pass
            await notify_state()             

        elif data['action'] == 'put':
        # 2 when they PUT: TBD: delete unmentioned values, also create new object 
        # throw error when theres no order_name 
            STATE['msg'] = data['in']
            STATE['msg'] = process_in(STATE['msg'])

            if 'order_name' not in STATE['msg']: 
                await websocket.send('Need order_name!')
                print('Need order_name!')
            else: 
                try: 
                    if ',' in STATE['msg']: 
                        put_ind = STATE['msg'].split(',')[0] + '}'
                        r = collection.delete_one(json.loads(put_ind))
                    else: 
                        r = collection.delete_one(json.loads(STATE['msg']))
                    collection.insert_one(json.loads(STATE['msg']))
                    if r.deleted_count == 0: 
                        await websocket.send('Bird didnt exist before. New Entry Created.')
                        print('Bird didnt exist before. New Entry Created.')
                    else: 
                        await websocket.send('Just Put in: ' + STATE['msg'])
                        print('Just Put in: ' + STATE['msg'])
                    print('Put Success! ')
                except Exception as e: 
                    await websocket.send('Failed to put! ' + str(e))
                    print('Failed to put! ' + str(e))
                await notify_state()

        elif data['action'] == 'insert':
        # POST command
        # 3 when they POST: 
        # will post error msg when order_name not in input 
            STATE['msg'] = data['in']
            STATE['msg'] = process_in(STATE['msg'])
            if 'order_name' not in STATE['msg']: 
                await websocket.send('Error! No order_name!')
                print('Error! No order_name!')
            if collection.find_one({"order_name":data["order_name"]}) != None:
                await websocket.send('Bird already exists!')
                print('Bird already exists!')
            else: 
                try: 
                    collection.insert_one(json.loads(STATE['msg']))
                    await websocket.send('Just Inserted: ' + STATE['msg'])
                    print('Just Inserted: ' + STATE['msg'])
                    print('Insert Success! ')
                except Exception as e: 
                    await websocket.send('Failed to insert! ' + str(e))
                    print('Failed to insert! ' + str(e))
                await notify_state()

        #PATCH command
        elif data['action'] == 'update':
            STATE['msg'] = data['in']
            STATE['msg'] = process_in(STATE['msg'])
        # 4, when they patch: 
        # when no order_name given, give error msg instead 
            index_upd = STATE['msg'].split(',')[0] + '}'
            if 'order_name' not in index_upd: 
                await websocket.send('Error! No order_name!')
                print('Error! No order_name!')
            if collection.find_one({"order_name":data["order_name"]}) == None:
                await websocket.send('Bird doesnt exists!')
                print('Bird doesnt exists!')
            else: 
                if data['code'] != '' and data['note'] != '': 
                    content_upd = '{"$set": {"code": "' + data['code'] + '" , "note": "' + data['note'] + '"}}'
                    try: 
                        collection.update_one(json.loads(index_upd), json.loads(content_upd))
                        await websocket.send('Just Updated: ' + STATE['msg'])
                        print('Just Updated: ' + STATE['msg'])
                        print('Update Success!')
                    except Exception as e: 
                        await websocket.send('Failed! ' + str(e))
                        print('Failed! ' + str(e))
                elif data['code'] != '': 
                    content_upd = '{"$set": {"code": "' + data['code'] + '"}}'
                    try: 
                        collection.update_one(json.loads(index_upd), json.loads(content_upd))
                        await websocket.send('Just Updated: ' + STATE['msg'])
                        print('Just Updated: ' + STATE['msg'])
                        print('Update Success!')
                    except Exception as e: 
                        await websocket.send('Failed! ' + str(e))
                        print('Failed! ' + str(e))
                elif data['note'] != '': 
                    content_upd = '{"$set": {"note": "' + data['note'] + '"}}'
                    try: 
                        collection.update_one(json.loads(index_upd), json.loads(content_upd))
                        await websocket.send('Just Updated: ' + STATE['msg'])
                        print('Just Updated: ' + STATE['msg'])
                        print('Update Success!')
                    except Exception as e: 
                        await websocket.send('Failed! ' + str(e))
                        print('Failed! ' + str(e))
                else: 
                    content_upd = '{"$set": {}}'
                    await websocket.send('Nothing is updated! ')
                    print('Nothing is updated!')
                await notify_state()

        elif data['action'] == 'delete': 
        # 5, when they delete: 
        # when trying to delete already deleted record, throw error message on webpage
            STATE['msg'] = data['in']
            STATE['msg'] = process_in(STATE['msg'])
            try: 
                result = collection.delete_one(json.loads('{"order_name": ' + '"'+data['order_name']+'"'+'}'))
                if result.deleted_count != 0: 
                    await websocket.send('Just Deleted: ' + '{"order_name": ' + '"'+data['order_name']+'"'+'}')
                    print('Just Deleted: ' + '{"order_name": ' + '"'+data['order_name']+'"'+'}')
                    print('Delete Success! ')
                else: 
                    await websocket.send('No record found! Maybe its already deleted?')
                    print('No record found! Maybe its already deleted?')
                    print('Already Deleted! ')
            except Exception as e: 
                await websocket.send('Deletion Failed! ' + str(e))
                print('Deletion Failed! ' + str(e))
            await notify_state()
        else:
            logging.error("unsupported event: {}", data)

start_server = websockets.serve(receive_from_html, 'localhost', 5000)
print('start success! ')

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

