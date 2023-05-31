import xmltodict, json

def xmljson(file):
    with open (file, "r") as f1:
        read = f1.read()

    start = read.find('<list')
    end = read.find('</list>') + len('</list>')
    read = read[start:end]

    o = xmltodict.parse(read)
    content = json.dumps(o) # '{"e": {"a": ["text", "text"]}}'
    #print(content[:500])

    f2 = open('test.json', 'w')
    f2.write(content)
    f2.close()

    with open('test.json', 'r') as f:
        data = json.load(f)

    data = data['list']['order']
    result = []
    for i in data:
        order_dict = {}
        order_name = i['latin_name']
        order_dict['order_name'] = order_name
        if 'code' in i.keys():
            order_dict['code'] = i['code']
        if 'note' in i.keys():
            order_dict['note'] = i['note']
        family_list = []
        if isinstance(i['family'], dict):
            family_dict = {}
            family_dict['family_name'] = i['family']['latin_name']
            family_dict['common_name'] = i['family']['english_name']
            if isinstance(i['family']['genus'], dict):
                family_dict['number_of_genus'] = 1
            if isinstance(i['family']['genus'], list):
                count_list = []
                for j in i['family']['genus']:
                    count_list.append(j['latin_name'])
                count = len(count_list)
                family_dict['number_of_genus'] = count
            family_list.append(family_dict)
            order_dict['family'] = family_list

        if isinstance(i['family'], list):
            for k in i['family']:
                family_dict = {}
                family_dict['family_name'] = k['latin_name']
                family_dict['common_name'] = k['english_name']
                if isinstance(k['genus'], dict):
                    family_dict['number_of_genus'] = 1
                if isinstance(k['genus'], list):
                    count_list = []
                    for j in k['genus']:
                        count_list.append(j['latin_name'])
                    count = len(count_list)
                    family_dict['number_of_genus'] = count    

                family_list.append(family_dict)
            order_dict['family'] = family_list

        result.append(order_dict)

    with open('order_family.json', 'w') as f:
        json.dump(result, f, indent=2)
