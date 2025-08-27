# standard imports
import unittest
import logging
import json
from email.message import Message

# local imports
from piknik import (
        Basket,
        Issue,
        )
from piknik.msg import IssueMessage

# test imports
from tests.common import TestStates
from tests.common import TestMsgStore

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


def test_wrapper(p):
    m = Message()
    m.add_header('Foo', 'bar')
    m.set_type('multipart/relative')
    m.set_payload(p)
    return m


def test_unwrapper(msg, message_callback=None, part_callback=None):
    for v in msg.walk():
        if message_callback != None:
            message_callback(v)


class TestMsg(unittest.TestCase):

    def setUp(self):
        self.store = TestStates()
        self.b = Basket(self.store)


    def test_basic(self):
        o = Issue('foo')
        v = IssueMessage(o)


    def test_single_content(self):
        o = Issue('foo')
        v = self.b.add(o)
        m = self.b.msg(v, 's:foo')


    def test_multi_content(self):
        o = Issue('foo')
        v = self.b.add(o)
        m = self.b.msg(v, 's:foo', 's:bar', 's:baz')


    def test_single_file_content(self):
        o = Issue('foo')
        v = self.b.add(o)
        m = self.b.msg(v, 'f:tests/one.png')


    def test_mixed_content(self):
        o = Issue('foo')
        v = self.b.add(o)
        m = self.b.msg(v, 's:bar')
        m = self.b.msg(v, 'f:tests/one.png')
        m = self.b.msg(v, 's:baz')
        m = self.b.msg(v, 'f:tests/two.bin')


    def test_wrapper(self):
        b = Basket(self.store, message_wrapper=test_wrapper)
        o = Issue('bar')
        v = b.add(o)
        m = b.msg(v, 's:foo')
        print(m)


    def test_render(self):
        b = Basket(self.store, message_wrapper=test_wrapper)
        o = Issue('bar')
        v = b.add(o)
        m = b.msg(v, 's:foo')
        m = b.msg(v, 's:bar', 's:baz')
 
        def render_envelope(msg, hdr):
            print('eeeeeenvvv {} {}'.format(hdr, msg))

        def render_message(envelope, msg, mid):
            print('rendeeeer {} {}'.format(mid, msg))

        m = b.get_msg(v, envelope_callback=render_envelope, message_callback=render_message)


    def test_render_alias(self):
        b = Basket(self.store, message_wrapper=test_wrapper)
        o = Issue('bar', alias='xyzzy')
        v = b.add(o)
        m = b.msg(v, 's:foo')
        m = b.msg(v, 's:bar', 's:baz')
 
        def render_envelope(msg, hdr):
            print('eeeeeenvvv {} {}'.format(hdr, msg))

        def render_message(envelope, msg, mid):
            print('rendeeeer {} {}'.format(mid, msg))

        m = b.get_msg('xyzzy', envelope_callback=render_envelope, message_callback=render_message)



if __name__ == '__main__':
    unittest.main()
