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


class DiscoverDeviceResource(resource.Resource):

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

            # Simple simulation of just returning a url and an id of a found device
            message_obj = Message(json_payload)
            device_id = registered_device.get(message_obj.device_capability)

            request_response_obj = {}
            request_response_obj['url'] = 'temp'
            request_response_obj['device_id'] = device_id

            response_payload = json.dumps(request_response_obj, cls=BytesDump).encode()
        except Exception as e:
            print(e)

        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)

