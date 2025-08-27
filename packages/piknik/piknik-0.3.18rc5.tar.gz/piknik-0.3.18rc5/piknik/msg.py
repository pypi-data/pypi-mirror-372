# standard imports
import logging
import uuid
import mimetypes
from base64 import b64encode
import time
from email.message import Message
from email import message_from_string
from email.policy import Compat32
from email.utils import formatdate
from email.utils import parsedate_to_datetime


logg = logging.getLogger(__name__)


class MessageEnvelope:

    def __init__(self, msg):
        self.msg = msg
        self.sender = None
        self.valid = False
        self.resolved = False


def rubber_stamp_envelope(envelope, envelope_type):
    envelope.valid = True
    return


class IssueMessage:

    def __init__(self, issue):
        self.__m = Message()

        self.__m.add_header('Subject', issue.title)
        self.__m.add_header('X-Piknik-Id', issue.id)
        self.__m.add_header('Date', formatdate(time.time()))
        self.__m.set_payload(None)
        self.__m.set_type('multipart/relative')
        self.__m.set_boundary(str(uuid.uuid4()))


    def __unwrap(self, msg, envelope_callback=rubber_stamp_envelope, message_callback=None, post_callback=None):
        message_ids = []
        message_id = None
        message_date = None
        envelope = None
        initial = False

        for m in msg.walk():
            if not initial:
                initial = True
                continue
            env_header = m.get('X-Piknik-Envelope')
            if env_header != None:
                if envelope_callback != None:
                    m = envelope_callback(m, env_header)
                envelope = m
                continue

            if message_callback == None:
                continue

            new_message_id = m.get('X-Piknik-Msg-Id')
            if new_message_id != None:
                message_id = new_message_id
                message_ids.append(message_id)
                d = m.get('Date')
                message_date = parsedate_to_datetime(d)
            message_callback(m, message_id, message_date)

        if post_callback != None:
            post_callback(message_ids)

        return message_ids


    @classmethod
    def parse(cls, issue, v, envelope_callback=None, message_callback=None, post_callback=None):
        o = cls(issue)
        m = message_from_string(v)
        o.__unwrap(m, envelope_callback=envelope_callback, message_callback=message_callback, post_callback=post_callback)
        o.__m = m
        return o


    def from_text(self, v):
        m = Message()
        m.add_header('Content-Transfer-Encoding', 'QUOTED-PRINTABLE')
        m.set_charset('UTF-8')
        m.set_payload(str(v))
        return m


    def detect_file(self, v):
        r = mimetypes.guess_type(v)
        if r[0] == None:
            return ('application/octet-stream', None,)
        return r


    def from_file(self, v):
        m = Message()
        
        mime_type = self.detect_file(v)
        m.set_type(mime_type[0])

        if mime_type[1] != None:
            m.set_charset(mime-type[1])
        m.add_header('Content-Transfer-Encoding', 'BASE64')
        m.add_header('Content-Disposition', 'attachment; filename="{}"'.format(v))

        f = open(v, 'rb')
        r = f.read()
        f.close()
        r = b64encode(r)
        m.add_header('Content-Length', str(len(r)))
        m.set_payload(r.decode())

        return m


    def add(self, *args, related_id=None, wrapper=None, message_id=None):
        m_id = None
        try:
            m_id = uuid.UUID(message_id)
        except (ValueError, TypeError):
            m_id = uuid.uuid4()
        m = Message()
        m.add_header('X-Piknik-Msg-Id', str(m_id))
        m.add_header('Date', formatdate(time.time()))
        if related_id != None:
            m.add_header('In-Reply-To', related_id)
        m.set_payload(None)
        m.set_type('multipart/mixed')
        m.set_boundary(str(uuid.uuid4()))
        for a in args:
            p = a[:2]
            v = a[2:]
            r = None
            if p == 'f:':
                r = self.from_file(v)
            elif p == 's:':
                r = self.from_text(v)
            m.attach(r)
        if wrapper:
            m = wrapper(m)
        self.__m.attach(m)


    def as_string(self, **kwargs):
        return self.__m.as_string(**kwargs)


    def as_bytes(self, **kwargs):
        return self.__m.as_bytes(**kwargs)


    def __str__(self):
        return self.as_string()
