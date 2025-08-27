# standard imports
import unittest
import logging
import json

# local imports
from piknik import Basket
from piknik import Issue
from piknik.identity import Identity
from piknik.error import UnknownIdentityError
from piknik.error import ExistsError

# tests imports
from tests.common import TestStates

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestAssign(unittest.TestCase):

    def setUp(self):
        self.alice = 'F3FAF668E82EF5124D5187BAEF26F4682343F692'
        self.bob = 'F645E047EE5BC4E2824C94DB42DC91CFA8ABA02B'


    def test_dep_basic(self):
        one = Issue('foo')
        one.dep('bar')
        one.dep('baz')
        with self.assertRaises(ExistsError):
            one.dep('bar')
        one.undep('bar')
        self.assertEqual(len(one.dependencies), 1)


    def test_dep_alias(self):
        one = Issue('foo', alias='inky')
        two = Issue('bar', alias='pinky')
        three = Issue('baz')
        self.b = Basket(TestStates())
        issue_id_one = self.b.add(one)
        issue_id_two = self.b.add(two)
        issue_id_three = self.b.add(three)
        self.b.dep('inky', 'pinky')
        self.b.dep(issue_id_three, 'inky')

        with self.assertRaises(ExistsError):
            self.b.dep(issue_id_one, 'pinky')

        with self.assertRaises(ExistsError):
            self.b.dep(issue_id_three, issue_id_one)


if __name__ == '__main__':
    unittest.main()
