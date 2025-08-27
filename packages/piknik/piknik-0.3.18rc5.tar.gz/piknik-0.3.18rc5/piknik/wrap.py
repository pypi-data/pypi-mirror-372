# standard imports
import logging
from base64 import b64decode

# external imports
from mimeparse import parse_mime_type

# local imports
from piknik.msg import MessageEnvelope

logg = logging.getLogger(__name__)


class Wrapper:

    def __init__(self, dump_dir=None):
        self.content_buffer = []
        self.envelope_state = -1 # -1 not in envelope, 0 in outer envelope, 1 inner envelope, not (yet) valid, 2 envelope valid (with signature)
        self.envelope = None
        self.dump_dir = dump_dir
        self.msg_idx = 0


    def process_envelope(self, msg, env_header):
        self.envelope = MessageEnvelope(msg)
        self.envelope_state = 0
        self.msg_idx = 0
        return self.envelope


    def process_message(self, msg, message_id, message_date):
        if msg.get('X-Piknik-Msg-Id') == None:
            self.add(self.envelope, message_id, msg)
        return (self.envelope, msg,)


    def add(self, envelope, message_id, message):
        m = parse_mime_type(message.get_content_type())
        filename = message.get_filename()

        v = None
        if filename == None:
            if m[0] == 'text':
                if m[1] == 'plain':
                    v = message.get_payload()
                    if message.get('Content-Transfer-Encoding') == 'BASE64':
                        v = b64decode(v).decode()
        else:
            v = message.get_payload()
            if message.get('Content-Transfer-Encoding') == 'BASE64':
                try:
                    v = b64decode(v).decode()
                except UnicodeDecodeError:
                    pass

            if self.dump_dir != None:
                (void, ext) = os.path.splitext(filename)
                (fp, fn) = tempfile.mkstemp(suffix=ext, dir=self.dump_dir)

                f = os.fdopen(fp, 'wb')
                try:
                    f.write(v)
                except TypeError:
                    f.write(v.encode('utf-8'))
                f.close()

                filename = fn

        sz = message.get('Content-Length')
        if sz == None:
            sz = -1
        else:
            sz = int(sz)

        o = {
                'envelope': envelope,
                'id': message_id,
                'type': m,
                'filename': filename,
                'size': sz,
                'contents': v,
                'idx': self.msg_idx,
                }
        self.msg_idx += 1

        self.content_buffer.append(o)


    def pop(self):
        try:
            return self.content_buffer.pop(0)
        except IndexError:
            return None
