import json_to_mongoDB
import xml_to_json
import sys

def main(file):
	xml_to_json.xmljson(file)
	json_to_mongoDB.jsonmongo()

if __name__ == '__main__':
	filename = sys.argv[1]
	main(filename)