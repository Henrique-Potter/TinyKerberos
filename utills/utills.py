import json
import time

from fernet import Fernet


class BytesDump(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode()
        return json.JSONEncoder.default(self, obj)


def create_access_ticket(session_key, rad_key):

    access_ticket_raw = {}

    access_ticket_raw['timeStamp'] = time.time()
    access_ticket_raw['session_key'] = session_key
    access_ticket_raw['session_id'] = Fernet.generate_key()

    rad_encryptor_engine = Fernet(rad_key)
    access_ticket_enc = rad_encryptor_engine.encrypt(json.dumps(access_ticket_raw, cls=BytesDump).encode())

    return access_ticket_enc

