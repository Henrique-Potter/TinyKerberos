import aiocoap.resource as resource
import aiocoap
from threading import Lock
import time

peyes_lock = Lock()


class TinyKerberosAuth(resource.Resource):

    def __init__(self):
        super().__init__()

    async def render_get(self, request):

        start1 = time.time()

        time.sleep(1)

        #self.payload = found_face

        print('Sleep Time: {}'.format(time.time() - start1))

        self.content = b"Some response"

        return aiocoap.Message(payload=self.content)


    async def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)

