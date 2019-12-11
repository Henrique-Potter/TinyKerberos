import aiocoap.resource as resource
import aiocoap
from threading import Lock
import time

from cryptography.fernet import Fernet

from domain.message import Message


# Simple Key-Value database of owner keys
from utills import create_access_ticket, json, BytesDump

registered_owners = {2: b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R5c='}

# Simple Key-Value database of users passwords
registered_users = {10: b'somesecretpassword'}

# Simple Key-Value database for device id
registered_device = {"temperature": 123}

# Simple Key-Value for device - owner relation
device_owner = {123: 2}

# Root RAD key to validate authentication tickets
rad_key = b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R8c='


class SecDiscoverDeviceResource(resource.Resource):

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
            enc_json_access_ticket = message_obj.access_ticket

            rad_encryptor = Fernet(rad_key)

            plain_json_access_ticket = rad_encryptor.decrypt(enc_json_access_ticket.encode())
            access_ticket_obj = Message(plain_json_access_ticket)

            client_id = access_ticket_obj.client_id
            users_pass = registered_users.get(client_id)

            if users_pass:

                session_key = access_ticket_obj.session_key

                session_encryptor = Fernet(session_key)

                # Finding device
                plain_json_request = session_encryptor.decrypt(message_obj.device_request.encode())
                request_object = Message(plain_json_request)
                device_id = registered_device.get(request_object.device_capability)

                owner_id = device_owner.get(device_id)
                owner_key = registered_owners.get(owner_id)

                # Creating ticket for rad approval (needs specific key other than rad_key)
                device_session_key = Fernet.generate_key()
                enc_json_rad_ticket = create_access_ticket(device_session_key, rad_key, client_id)

                # Creating ticket for owner approval (needs specific key other than owner_key)
                enc_json_owner_ticket = create_access_ticket(device_session_key, owner_key, client_id)

                request_response_obj = {}
                request_response_obj['url'] = 'temp'
                request_response_obj['device_session_key'] = device_session_key
                request_response_obj['rad_ticket'] = enc_json_rad_ticket
                request_response_obj['owner_ticket'] = enc_json_owner_ticket

                enc_request_response_obj = session_encryptor.encrypt(json.dumps(request_response_obj, cls=BytesDump).encode())

                response_payload = json.dumps(enc_request_response_obj, cls=BytesDump).encode()
            else:
                response_payload = b"401"

        except Exception as e:
            print(e)

        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)

