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
from piknik.render.html import Renderer
from piknik.render.html import Accumulator
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
    m.add_header('X-Piknik-Envelope', 'foo')
    m.set_type('multipart/relative')
    m.set_payload(p)
    return m


class TestMsg(unittest.TestCase):

    def setUp(self):
        (self.crypto, self.gpg, self.gpg_dir) = pgp_setup()
        self.store = TestStates()
        self.b = Basket(self.store, message_wrapper=self.crypto.sign)
        self.render_dir = tempfile.mkdtemp()


    def tearDown(self):
        shutil.rmtree(self.render_dir)


    def test_states_two_issues(self):
        issue_one = Issue('foo')
        self.b.add(issue_one)

        issue_two = Issue('bar')
        v = self.b.add(issue_two)

        m = self.b.msg(v, 's:foo')

        state = self.b.get_state(v)

        msgs = []
        w = io.StringIO()
        renderer = Renderer(self.b, outdir=self.render_dir)
        renderer.apply()


    def test_issue(self):
        issue = Issue('foo')
        issue_id = self.b.add(issue)

        m = self.b.msg(issue_id, 's:foo')

        self.b.tag(issue_id, 'inky')
        self.b.tag(issue_id, 'pinky')

        state = self.b.get_state(issue_id)
        tags = self.b.tags(issue_id)

        w = io.StringIO()
        acc = Accumulator(w=w)
        wrapper = Wrapper()
        renderer = Renderer(self.b, outdir=self.render_dir, wrapper=wrapper, accumulator=acc.add)
        renderer.apply_begin()
        renderer.apply_issue(state, issue, tags)
        renderer.apply_end()

        w.seek(0)
        print(w.read())


    def test_issue_attachment(self):
        b = Basket(self.store, message_wrapper=test_wrapper)
        issue = Issue('foo')
        issue_id = b.add(issue)

        m = b.msg(issue_id, 'f:tests/three.webp')

        state = b.get_state(issue_id)
        tags = []

        w = io.StringIO()
        acc = Accumulator(w=w)
        wrapper = Wrapper()
        renderer = Renderer(b, outdir=self.render_dir, wrapper=wrapper, accumulator=acc.add)
        renderer.apply_begin()
        renderer.apply_issue(state, issue, tags)
        renderer.apply_end()

        w.seek(0)
        print(w.read())



if __name__ == '__main__':
    unittest.main()
