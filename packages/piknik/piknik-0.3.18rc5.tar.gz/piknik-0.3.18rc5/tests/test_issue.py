# standard imports
import unittest
import logging
import json

# local imports
from piknik import Issue
from piknik.identity import Identity

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestIssue(unittest.TestCase):

    def test_basic(self):
        o = Issue('foo')
        r = json.loads(str(o))
        self.assertEqual(str(o.id), r['id'])
        self.assertEqual(o.title, r['title'])


    def test_basic_from_str(self):
        o = Issue('foo')
        v = str(o)
        r = Issue.from_str(v)
        self.assertTrue(o == r)


if __name__ == '__main__':
    unittest.main()
