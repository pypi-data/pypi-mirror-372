# standard imports
import unittest
import logging

# external imports
import shep

# local imports
from piknik import (
        Basket,
        Issue,
        )
from piknik.error import DeadIssue

# tests imports
from tests.common import debug_out
from tests.common import TestStates

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestBasic(unittest.TestCase):

    def setUp(self):
        self.b = Basket(TestStates())

    
    def test_issue_basic(self):
        o = Issue('The first issue')
        v = self.b.add(o)
        self.assertEqual(v, str(o.id))
        r = self.b.get(v)
        self.assertEqual(r, o)


    def test_list(self):
        o = Issue('The first issue')
        self.b.add(o)
        o = Issue('The second issue')
        self.b.add(o)
        r = self.b.list('proposed')
        self.assertEqual(len(r), 2)


    def test_progres(self):
        o = Issue('The first issue')
        v = self.b.add(o)
        self.b.advance(v)
        self.b.advance(v)
        self.b.advance(v)
        self.b.advance(v)
        self.b.advance(v)
        with self.assertRaises(DeadIssue):
            self.b.advance(v)
            

    def test_list_jump(self):
        o = Issue('The first issue')
        v = self.b.add(o)
        o_two = Issue('The second issue')
        v_two = self.b.add(o_two)
        self.b.advance(v_two)
        o_three = Issue('The second issue')
        self.b.add(o_three)
        self.b.state_doing(v)

        r = self.b.list('proposed')
        self.assertEqual(len(r), 1)

        r = self.b.list('backlog')
        self.assertEqual(len(r), 1)

        r = self.b.list('doing')
        self.assertEqual(len(r), 1)


    def test_jump(self):
        o = Issue('The first issue')
        v = self.b.add(o)
        self.b.state_doing(v)
        r = self.b.list('doing')
        self.assertEqual(len(r), 1)
        self.b.state_review(v)
        r = self.b.list('review')
        self.assertEqual(len(r), 1)
        self.b.state_backlog(v)
        r = self.b.list('backlog')
        self.assertEqual(len(r), 1)
        self.b.state_finish(v)
        r = self.b.list('finished')
        self.assertEqual(len(r), 1)


    def test_magic_unblock(self):
        o = Issue('The first issue')
        v = self.b.add(o)
        self.b.advance(v)
        self.b.advance(v)
        self.b.block(v)
        self.assertIn(v, self.b.blocked())
        self.b.advance(v)
        self.assertNotIn(v, self.b.blocked())


    def test_no_resurrect(self):
        o = Issue('The first issue')
        v = self.b.add(o)
        self.b.state_finish(v)
        with self.assertRaises(DeadIssue):
            self.b.state_doing(v)


    def test_states_list(self):
        r = self.b.states()
        self.assertEqual(len(r), 7)


    def test_alias(self):
        o = Issue('The first issue', alias="first")
        issue_id = o.id
        v = self.b.add(o)
        o = self.b.get("first")
        self.assertEqual(o.id, issue_id)
        self.b.state_finish(issue_id)
        with self.assertRaises(FileNotFoundError):
            o = self.b.get("first")

if __name__ == '__main__':
    unittest.main()
