import asyncio
import platform
import logging
import argparse

import aiocoap.resource as resource
import aiocoap

#if platform.uname()[1] == 'raspberrypi':
from coapresources import SecRegisterDeviceResource, DeviceInteractionResource
from coapresources import DiscoverDeviceResource
from coapresources import SecDeviceInteractionResource
from coapresources import SecDiscoverDeviceResource
from coapresources import SecAuthUserResource
from coapresources import RegisterDeviceResource

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=False)
    args = parser.parse_args()

    # Resource tree creation
    root = resource.Site()
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('register',), RegisterDeviceResource())
    root.add_resource(('sec_register',), SecRegisterDeviceResource())
    root.add_resource(('sec_auth_user',), SecAuthUserResource())
    root.add_resource(('sec_discover',), SecDiscoverDeviceResource())
    root.add_resource(('discover',), DiscoverDeviceResource())
    root.add_resource(('sec_temp',), SecDeviceInteractionResource())
    root.add_resource(('temp',), DeviceInteractionResource())


    # Not being used
    server_address = args.ip

    try:
        #asyncio.Task(aiocoap.Context.create_server_context(root, bind=("", 5683)))

        # it will bind to all available IPs
        server_context = aiocoap.Context.create_server_context(root)
        asyncio.Task(server_context)

        print("IP bound to localhost")
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



