# standard imports
import unittest
import logging
import json

# local imports
from piknik import Issue
from piknik.identity import Identity
from piknik.error import UnknownIdentityError

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestAssign(unittest.TestCase):

    def setUp(self):
        self.alice = 'F3FAF668E82EF5124D5187BAEF26F4682343F692'
        self.bob = 'F645E047EE5BC4E2824C94DB42DC91CFA8ABA02B'


    def test_identity_pointer(self):
        check = "sha256:65ea9b0609341322903823660bf45326f473d903ee7d327dff442f46d68eacd9"
        p = Identity(self.alice)
        r = p.uri()
        self.assertEqual(r, check)


    def test_identity_load(self):
        o = Issue('foo')
        alice = Identity(self.alice)
        o.assign(alice)
        bob = Identity(self.bob)
        o.assign(bob)
        r = o.get_assigned()
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0][0], alice)
        self.assertEqual(r[1][0], bob)
        self.assertGreater(r[1][1], r[0][1])


    def test_identity_assigned_from_str(self):
        o = Issue('foo')
        alice = Identity(self.alice)
        bob = Identity(self.bob)
        o.assign(alice)
        o.assign(bob)
        v = str(o)
        r = Issue.from_str(v)
        self.assertTrue(o == r)

        check = r.get_assigned()
        self.assertEqual(len(check), 2)


    def test_identity_set_owner(self):
        o = Issue('foo')
        alice = Identity(self.alice)
        bob = Identity(self.bob)
        o.assign(alice)
        o.assign(bob)

        r = o.owner()
        self.assertEqual(r, alice)

        o.set_owner(bob)
        r = o.owner()
        self.assertEqual(r, bob)


    def test_identity_unassign(self):
        o = Issue('foo')
        alice = Identity(self.alice)
        bob = Identity(self.bob)
        o.assign(alice)
        o.assign(bob)
   
        o.unassign(alice)
        r = o.get_assigned()
        self.assertEqual(len(r), 1)

        r = o.owner()
        self.assertEqual(r, bob)

        with self.assertRaises(UnknownIdentityError):
            o.unassign(alice)

        o.unassign(bob)
        with self.assertRaises(UnknownIdentityError):
            o.owner()


    def test_issue_identity_equality(self):
        alice = Identity(self.alice)
        bob = Identity(self.bob)

        one = Issue('foo')
        two = Issue('foo', issue_id=one.id)

        one.assign(alice)
        two.assign(alice)
        self.assertTrue(one == two)

        two.assign(bob)
        self.assertFalse(one == two)
        

if __name__ == '__main__':
    unittest.main()
