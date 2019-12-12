import asyncio
from aiocoap import *
from cryptography.fernet import Fernet
import json

import utills
from domain.message import Message as msg
from utills.utills import BytesDump
from pathlib import Path

current_dir = Path(__file__).parent.absolute()

host = "192.168.0.141"
host_note = "192.168.0.177"

port = 5683
path_identify = "auth"
path_learn = "peyes"

owner_key = b"A9KQBzD07VToOFSSkpnXI0TuYalsTtSZePPf0cq1R5c="


# Debug Function
async def get_call():

    protocol = await Context.create_client_context()

    request = Message(code=GET)

    #request.set_request_uri(uri='coap://192.168.0.177:5683/auth')
    request.set_request_uri(uri='coap://[::1]:5683/auth')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))


# Secure version of device registration method
async def sec_register_device_put_call():

    protocol = await Context.create_client_context()

    # This should have been created during the device NFC registration
    device_id = Fernet.generate_key()
    device_owner_key = Fernet.generate_key()

    owner_encryptor = Fernet(owner_key)
    secure_device_id = owner_encryptor.encrypt(device_id)

    payload_dict = {}
    payload_dict["owner_uuid"] = 2
    payload_dict["device_id"] = secure_device_id

    payload = json.dumps(payload_dict, cls=BytesDump).encode()

    request = Message(code=PUT, payload=payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/sec_register')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))


# Non-secure version of device registration method
async def register_device_put_call():

    protocol = await Context.create_client_context()

    # This should have been created during the device NFC registration
    device_id = Fernet.generate_key()

    owner_encryptor = Fernet(owner_key)

    payload_dict = {}
    payload_dict["owner_uuid"] = 2
    payload_dict["device_id"] = device_id

    payload = json.dumps(payload_dict, cls=BytesDump).encode()

    request = Message(code=PUT, payload=payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/register')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))


# Secure version of client authentication method
async def sec_client_auth_put_call():

    protocol = await Context.create_client_context()

    password = b"somesecretpassword"

    # Simple proof of secret key ownership
    token = utills.encrypt_with_password(password, password)

    payload_dict = {}
    payload_dict["user_id"] = 10
    payload_dict["token"] = token

    payload = json.dumps(payload_dict, cls=BytesDump).encode()

    request = Message(code=PUT, payload=payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/sec_auth_user')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload_enc = response.payload

        # Decrypting with Fernet custom password-based key
        payload = utills.decrypt_with_password(password, payload_enc)

        # Loading Json as Python object
        message = msg(payload)

        # Retrieving session key and access ticket
        session_key = message.session_key
        access_ticket = message.access_ticket

        return session_key, access_ticket


# Secure version of client device discovery method
async def sec_client_discover_device_put_call(session_key, access_ticket):

    protocol = await Context.create_client_context()

    device_request = {}
    device_request["device_capability"] = 'temperature'
    device_request["client_id"] = 10

    enc_json_device_request = utills.encrypt(session_key, json.dumps(device_request, cls=BytesDump).encode())

    request_payload_obj = {}
    request_payload_obj["device_request"] = enc_json_device_request
    request_payload_obj["access_ticket"] = access_ticket

    json_payload = json.dumps(request_payload_obj, cls=BytesDump).encode()

    request = Message(code=PUT, payload=json_payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/sec_discover')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload_enc = response.payload

        # Decrypting with Fernet custom password-based key
        payload = utills.decrypt(session_key, payload_enc)

        # Loading Json as Python object
        message = msg(payload)

        # Retrieving session key and access ticket
        url = message.url
        device_session_key = message.device_session_key
        rad_ticket = message.rad_ticket
        owner_ticket = message.owner_ticket

        return url, device_session_key, rad_ticket, owner_ticket


# Non-secure version of client device discovery method
async def client_discover_device_put_call():

    protocol = await Context.create_client_context()

    device_request_obj = {}
    device_request_obj["device_capability"] = 'temperature'

    json_payload = json.dumps(device_request_obj, cls=BytesDump).encode()

    request = Message(code=PUT, payload=json_payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/discover')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload_plain_text = response.payload

        # Loading Json as Python object
        message_object = msg(payload_plain_text)

        # Retrieving session key and access ticket
        url = message_object.url

        return url


# Secure version of client device interaction method
async def sec_client_device_interaction_put_call(url, device_session_key, rad_ticket, owner_ticket):

    protocol = await Context.create_client_context()

    device_data_request = {}
    device_data_request["capability"] = 'temp'
    device_data_request["client_id"] = 2

    enc_json_device_request = utills.encrypt(device_session_key, json.dumps(device_data_request, cls=BytesDump).encode())

    request_payload_obj = {}
    request_payload_obj["rad_ticket"] = rad_ticket
    request_payload_obj["owner_ticket"] = owner_ticket
    request_payload_obj["sensor_data_request"] = enc_json_device_request

    json_payload = json.dumps(request_payload_obj, cls=BytesDump).encode()

    request = Message(code=PUT, payload=json_payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/{}'.format(url))

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload_enc = response.payload

        # Decrypting with Fernet custom password-based key
        payload = utills.decrypt(device_session_key, payload_enc)

        # Loading Json as Python object
        message = msg(payload)

        # Retrieving session key and access ticket
        device_data = message.value


# Secure version of client device interaction method
async def client_device_interaction_put_call(url):

    protocol = await Context.create_client_context()

    device_data_request = {}
    device_data_request["capability"] = 'temp'

    json_payload = json.dumps(device_data_request, cls=BytesDump).encode()

    request = Message(code=PUT, payload=json_payload)
    request.set_request_uri(uri='coap://192.168.0.134:5683/{}'.format(url))

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)
        protocol.shutdown()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload = response.payload

        # Loading Json as Python object
        message = msg(payload)
        # Retrieving session key and access ticket
        device_data = message.value


def generate_device_id_and_key():

    device_id = Fernet.generate_key()
    device_key = Fernet.generate_key()

    return device_id, device_key


if __name__ == "__main__":

    #    session_key, access_ticket = asyncio.get_event_loop().run_until_complete(sec_client_auth_put_call())
    #    url, device_session_key, rad_ticket, owner_ticket = asyncio.get_event_loop().run_until_complete(sec_client_discover_device_put_call(session_key, access_ticket))
    #    asyncio.get_event_loop().run_until_complete(sec_client_device_interaction_put_call(url, device_session_key, rad_ticket, owner_ticket))

    url = asyncio.get_event_loop().run_until_complete(client_discover_device_put_call())

    asyncio.get_event_loop().run_until_complete(client_device_interaction_put_call(url))

