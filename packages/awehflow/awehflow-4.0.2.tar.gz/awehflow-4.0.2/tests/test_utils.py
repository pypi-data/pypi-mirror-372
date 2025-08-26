from unittest import TestCase
from unittest.mock import patch

from awehflow.utils import merge_dicts
from awehflow.utils import random_string
from awehflow.utils import uniquify_name


class TestUtils(TestCase):

    def test_merge_dicts(self):
        self.assertEqual(merge_dicts({'a': 1}, {'b': 2}), {'a': 1, 'b': 2})

    def test_nested_merge_dicts(self):
        self.assertEqual(merge_dicts({
            'a': 1,
            'c': {
                'd': 5,
                'e': 6
            }
        },
        {
            'b': 2,
            'c': {
                'e': 7
            }
        }), {
            'a': 1,
            'b': 2,
            'c': {
                'd': 5,
                'e': 7
            }
        })

    def test_random_string(self):
        str1 = random_string(string_length=10)
        self.assertEqual(len(str1), 10)

        str2 = random_string(string_length=20)
        self.assertEqual(len(str2), 20)

        str3 = random_string(string_length=20)
        self.assertNotEqual(str2, str3)

    @patch('awehflow.utils.random_string', return_value='bla_bla_bla')
    def test_uniquify_name(self, random_string_mock):
        self.assertEqual(uniquify_name('some_name'), 'some_name_bla_bla_bla')
