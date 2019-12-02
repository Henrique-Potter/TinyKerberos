import asyncio
import platform
import logging
import argparse

import aiocoap.resource as resource
import aiocoap

#if platform.uname()[1] == 'raspberrypi':

#from peyes_c_resource import PeyesC
from tiny_kerberos_res import TinyKerberosAuth


logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    args = parser.parse_args()

    # Resource tree creation
    root = resource.Site()
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))
    #root.add_resource(('peyes',), TinyKerberosAuth())

    # root.add_resource(('other', 'block'), BlockResource())
    # root.add_resource(('other', 'separate'), SeparateLargeResource())

    #server_address = args.ip
    server_address = 'fe80::785b:a177:34c0:d626%11'

    try:
        print("Server Started at {}".format(server_address))
        #asyncio.Task(aiocoap.Context.create_server_context(root))
        asyncio.Task(aiocoap.Context.create_server_context(root, bind=(server_address, 5683)))
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        print("Server Shutdown")
        asyncio.get_event_loop().stop()
        print("Exiting...")

        if platform.uname()[1] =='raspberrypi':
            import RPi.GPIO as GPIO
            GPIO.cleanup()


if __name__ == "__main__":
    main()



