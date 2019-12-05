import json


class Message:

    def __init__(self, json_data):
        # self.content = content
        # self.tiny_ticket = tiny_ticket
        # self.owner_uuid = None
        # self.device_id = None
        self.__dict__ = json.loads(json_data)

    def verify_ticket(self, key):
        return True

