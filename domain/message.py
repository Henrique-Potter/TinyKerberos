import json


# Simple class to generate dynamic objects from json data
class Message:
    def __init__(self, json_data):
        self.__dict__ = json.loads(json_data)



