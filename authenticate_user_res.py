import aiocoap.resource as resource
import aiocoap
from threading import Lock
import time
import json

from cryptography.fernet import Fernet

import utills
from domain.message import Message
from utills import BytesDump

peyes_lock = Lock()


# Simple Key-Value database of users passwords
registered_users = {10: b'somesecretpassword'}

# Simple key-value pair as common device-key token generator
device_key = b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R6c='


# Root RAD key to generate authentication tickets
rad_key = b'A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R8c='

class AuthUserResource(resource.Resource):

    def __init__(self):
        super().__init__()

    async def render_get(self, request):

        start1 = time.time()

        time.sleep(1)

        print('Sleep Time: {}'.format(time.time() - start1))

        self.content = b"Get method not implement for AuthUserResource"

        return aiocoap.Message(payload=self.content)

    async def render_put(self, request):

        print('PUT payload: %s' % request.payload)

        try:
            payload = request.payload
            message = Message(payload)

            # Dynamic attribute generated from json dump
            user_id = message.user_id
            user_token = message.token
            user_pass = registered_users.get(user_id)

            token_content = utills.decrypt(user_pass, user_token)

            response_dict = {}
            access_ticket_raw = {}

            # Simple user verification for now
            # If passwords match
            if token_content == user_pass:

                access_ticket_raw['timeStamp'] = time.time()
                access_ticket_raw['session_id'] = Fernet.generate_key()

                rad_enc_suite = Fernet(rad_key)

                access_ticket_enc = rad_enc_suite.encrypt(json.dumps(access_ticket_raw, cls=BytesDump).encode())

                response_dict['access_ticket'] = access_ticket_enc

                response_dict['session_key'] = Fernet.generate_key()

                response_payload = utills.encrypt(user_pass, json.dumps(response_dict, cls=BytesDump).encode())

            else:
                response_payload = b"401"

        except Exception as e:
            print(e)

        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)

