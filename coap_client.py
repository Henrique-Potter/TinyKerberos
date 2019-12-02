import logging
import asyncio
from aiocoap import *
import json
import time

host = "192.168.0.141"
host_note = "192.168.0.177"

port = 5683
path_identify = "auth"
path_learn = "peyes"


async def main():
    protocol = await Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri(uri='coap://[::ffff:10.0.2.15]:5683/auth')

    try:
        response = await protocol.request(request).response
        print(response.remote.hostinfo)

    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))


if __name__ == "__main__":

    asyncio.get_event_loop().run_until_complete(main())

