import asyncio
from aiocoap import *
from cryptography.fernet import Fernet
import json

from domain.message import Message as msg
import utills

host = "192.168.0.141"
host_note = "192.168.0.177"

port = 5683
path_identify = "auth"
path_learn = "peyes"

owner_key = b"A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R5c="


async def get_call():
    protocol = await Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri(uri='coap://[::1]:5683/auth')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)

    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))


async def register_device_put_call():

    protocol = await Context.create_client_context()

    # This should have been created during the device NFC registration
    device_id = Fernet.generate_key()
    device_owner_key = Fernet.generate_key()

    owner_encryption_suite = Fernet(owner_key)
    secure_device_id = owner_encryption_suite.encrypt(device_id)

    payloa_dict = {}
    payloa_dict["owner_uuid"] = 2
    payloa_dict["device_id"] = secure_device_id

    payload = json.dumps(payloa_dict, cls=utills.BytesDump).encode()

    request = Message(code=PUT, payload=payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/register')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)

    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))


async def client_auth_put_call():

    protocol = await Context.create_client_context()

    password = b"somesecretpassword"

    token = utills.encrypt(password, password)

    payload_dict = {}
    payload_dict["user_id"] = 10
    payload_dict["token"] = token

    payload = json.dumps(payload_dict, cls=utills.BytesDump).encode()

    request = Message(code=PUT, payload=payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/auth_user')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)

    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload_enc = response.payload

        # Decrypting with Fernet custom password-based key
        payload = utills.decrypt(password, payload_enc)

        # Loading Json as Python object
        message = msg(payload)

        # Retrieving session and access ticket keys
        session_key = message.session_key
        access_ticket = message.access_ticket

        print('Result: %s\n%r' % (response.code, response.payload))


def generate_device_id_and_key():

    device_id = Fernet.generate_key()
    device_key = Fernet.generate_key()

    return device_id, device_key


if __name__ == "__main__":

    #asyncio.get_event_loop().run_until_complete(get_call())
    #asyncio.get_event_loop().run_until_complete(register_device_put_call())
    asyncio.get_event_loop().run_until_complete(client_auth_put_call())

