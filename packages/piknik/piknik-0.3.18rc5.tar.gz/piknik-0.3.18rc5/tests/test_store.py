# standard imports
import unittest
import logging
import tempfile
import shutil
# external imports
import shep

# local imports
from piknik import (
        Basket,
        Issue,
        )
from piknik.error import DeadIssue
from piknik.store import FileStoreFactory
from piknik.identity import Identity

# tests imports
from tests.common import debug_out
from tests.common import TestStates
from tests.common import pgp_setup


logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


def debug_out(self, k, v):
    logg.debug('TRACE: {} {}'.format(k, v))


class TestStore(unittest.TestCase):

    def setUp(self):
        self.d = tempfile.mkdtemp()
        logg.debug('tempdir is {}'.format(self.d))
        self.store_factory = FileStoreFactory(self.d)
        self.b = Basket(self.store_factory)


    def tearDown(self):
        shutil.rmtree(self.d)
        pass


    # TODO: assert
    def test_basic(self):
        o = Issue('foo')
        v = self.b.add(o)


    # TODO: assert
    def test_load(self):
        o = Issue('foo')
        va = self.b.add(o)

        o = Issue('bar')
        vb = self.b.add(o)
        
        self.b.advance(va)

        b = Basket(self.store_factory)
        r = b.get(va)


    def test_load_tag(self):
        o = Issue('foo')
        va = self.b.add(o)
        self.b.tag(va, 'inky')
        self.b.tag(va, 'pinky')

        b = Basket(self.store_factory)
        r = b.tags(va)
        self.assertIn('INKY', r)
        self.assertIn('PINKY', r)

        self.b.untag(va, 'inky')
        b = Basket(self.store_factory)
        r = b.tags(va)
        self.assertNotIn('INKY', r)
        self.assertIn('PINKY', r)


    # TODO: assert
    def test_msg_putget(self):
        o = Issue('foo')
        issue_id = self.b.add(o)
        m = self.b.msg(issue_id, 's:bar')


    # TODO: assert
    def test_msg_resume(self):
        o = Issue('foo')
        v = self.b.add(o)
        m = self.b.msg(v, 's:bar')

        b = Basket(self.store_factory)
        m = b.msg(v, 's:baz')


    def test_msg_sig_verify_resume(self):
        (crypto, gpg, gpg_dir) = pgp_setup()
        b = Basket(self.store_factory, message_wrapper=crypto.sign)
        o = Issue('foo')
        v = b.add(o)
        r = b.msg(v, 's:foo', 's:bar')

        b = Basket(self.store_factory, message_wrapper=crypto.sign)
        m = b.get_msg(v)


    def test_store_assignments(self):
        o = Issue('foo')
        vb = self.b.add(o)
   
        alice = b'inky'.hex()
        bob = b'pinky'.hex()

        self.b.assign(vb, alice)
        self.b.assign(vb, bob)
        self.b.owner(vb, bob)
        r = self.b.get(vb)
        check = Identity(bob)
        self.assertTrue(r.owner() == check)

        self.b.unassign(vb, alice)

        r = self.b.get(vb)
        check = Identity(bob)
        self.assertEqual(r.owner(), check)
        check_assigned = r.get_assigned()
        self.assertTrue(r.owner() == check)


if __name__ == '__main__':
    unittest.main()
