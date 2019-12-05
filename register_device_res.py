import aiocoap.resource as resource
import aiocoap
from threading import Lock
import time

from cryptography.fernet import Fernet

from domain.message import Message

peyes_lock = Lock()


# Simple Key-Value database of owner keys
registered_owners = {2: b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R5c='}

# Simple Key-Value database of devices
registered_devices = {}


class RegisterDeviceResource(resource.Resource):

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
            payload = request.payload
            message = Message(payload)

            # Dynamic attribute generated from json dump
            owner_id = message.owner_uuid
            owner_key = registered_owners.get(owner_id)

            owner_encryption_suite = Fernet(owner_key)

            # Dynamic attribute generated from json dump
            secure_device_id = message.device_id.encode()
            plain_text_device_id = owner_encryption_suite.decrypt(secure_device_id)

            registered_devices[owner_id] = {plain_text_device_id: b''}

            authentication = True

            if authentication:
                response_payload = b"201"
            else:
                response_payload = b"401"

        except Exception as e:
            print(e)

        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)

