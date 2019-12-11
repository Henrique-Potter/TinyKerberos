from random import randrange

import aiocoap.resource as resource
import aiocoap
import time

from cryptography.fernet import Fernet
from domain.message import Message

# Simple Key-Value database of owner keys
from utills import json, BytesDump

registered_owners = {2: b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R5c='}

# Simple Key-Value database of users passwords
registered_users = {10: b'somesecretpassword'}

# Simple Key-Value database for device id
registered_device = {"temperature": 123}

# Simple Key-Value for device - owner relation
device_owner = {123: 2}

# Root RAD key to validate authentication tickets
rad_key = b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R8c='


class SecDeviceInteractionResource(resource.Resource):

    def __init__(self):
        super().__init__()

    async def render_get(self, request):

        start1 = time.time()

        time.sleep(1)

        print('Sleep Time: {}'.format(time.time() - start1))

        self.content = b"This is the get method"

        return aiocoap.Message(payload=self.content)

    async def render_put(self, request):

        print('PUT payload: %s' % request.payload)

        try:
            json_payload = request.payload
            message_obj = Message(json_payload)

            # Dynamic attribute generated from json dump
            enc_json_rad_ticket = message_obj.rad_ticket
            enc_json_owner_ticket = message_obj.owner_ticket

            # Validating ticket with key shared between device and rad
            # Exception is thrown if fails
            rad_encryptor = Fernet(rad_key)
            plain_json_rad_ticket = rad_encryptor.decrypt(enc_json_rad_ticket.encode())

            # Validating ticket with key shared between device and rad
            # Exception is thrown if fails
            owner_key = registered_owners.get(2)
            owner_encryptor = Fernet(owner_key)
            plain_json_owner_key = owner_encryptor.decrypt(enc_json_owner_ticket.encode())

            rad_ticket_obj = Message(plain_json_rad_ticket)

            session_key = rad_ticket_obj.session_key
            session_encryptor = Fernet(session_key)
            plain_json_request = session_encryptor.decrypt(message_obj.sensor_data_request.encode())

            # Generating fake sensor reading encrypting with the session key and returning to the client.
            random_temp_value = randrange(0, 50)
            request_response_obj = {}
            request_response_obj['value'] = random_temp_value

            enc_request_response_obj = session_encryptor.encrypt(json.dumps(request_response_obj, cls=BytesDump).encode())

            response_payload = json.dumps(enc_request_response_obj, cls=BytesDump).encode()

        except Exception as e:
            print(e)

        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)

