# standard imports
import unittest
import logging
import json
import shutil
import io
import tempfile
from email.message import Message
from email.utils import localtime as email_localtime

# external imports
from mimeparse import parse_mime_type

# local imports
from piknik import (
        Basket,
        Issue,
        )
from piknik.msg import IssueMessage
from piknik.render.base import Renderer
from piknik.wrap import Wrapper

# test imports
from tests.common import TestStates
from tests.common import TestMsgStore
from tests.common import pgp_setup

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


def test_wrapper(p):
    m = Message()
    m.add_header('Foo', 'bar')
    m.set_type('multipart/relative')
    m.add_header('X-Piknik-Envelope', 'foo')
    m.set_payload(p)
    return m


def test_unwrapper(msg, message_callback=None, part_callback=None):
    for v in msg.walk():
        if message_callback != None:
            message_callback(v)


class TestRenderer(Renderer):

    def __init__(self, basket, accumulator=None):
        super(TestRenderer, self).__init__(basket, accumulator=accumulator, wrapper=Wrapper())
        self.p = 0
        self.e = 0


    def apply_envelope(self, state, issue, tags, envelope, accumulator=None):
        r = self.e
        self.e += 1
        return r


    def apply_message_part(self, state, issue, tags, envelope, message, message_date, message_content, accumulator=None):
        r = self.p
        self.p += 1
        return r


class TestRendererComposite(TestRenderer):

    def __init__(self, basket, accumulator=None):
        super(TestRendererComposite, self).__init__(basket, accumulator=accumulator)
        self.last_message_id = None
        self.m = []


    def apply_message_post(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        if self.last_message_id != message_id:
            self.m.append(message_id)
            self.last_message_id = message_id


class TestMsg(unittest.TestCase):

    def setUp(self):
        self.acc = []
        self.store = TestStates()
        self.b = Basket(self.store, message_wrapper=test_wrapper)
        self.render_dir = tempfile.mkdtemp()


    def accumulate(self, v):
        self.acc.append(v)


    def tearDown(self):
        shutil.rmtree(self.render_dir)


    def test_idlepass(self):
        wrapper = Wrapper()
        renderer = TestRenderer(self.b, accumulator=self.accumulate)
        issue_one = Issue('foo')
        self.b.add(issue_one)

        issue_two = Issue('bar')
        v = self.b.add(issue_two)

        m = self.b.msg(v, 's:foo')

        renderer.apply()
        self.assertEqual(len(self.acc), 2)
        self.assertEqual(renderer.e, 1)
        self.assertEqual(renderer.p, 1)


    def test_composite(self):
        renderer = TestRendererComposite(self.b, accumulator=self.accumulate)
        issue_one = Issue('foo')
        self.b.add(issue_one)

        issue_two = Issue('bar')
        v = self.b.add(issue_two)

        m = self.b.msg(v, 's:foo')

        renderer.apply()
        self.assertEqual(len(renderer.m), 1)


    def test_attachment(self):
        renderer = TestRendererComposite(self.b, accumulator=self.accumulate)
        issue_one = Issue('foo')
        self.b.add(issue_one)

        issue_two = Issue('bar')
        v = self.b.add(issue_two)

        m = self.b.msg(v, 'f:tests/one.png')

        renderer.apply()
        self.assertEqual(len(renderer.m), 1)


if __name__ == '__main__':
    unittest.main()
