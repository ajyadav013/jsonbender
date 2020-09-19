import unittest

import sys

from jsonbender import S, K
from jsonbender.core import bend, BendingException, Context
from jsonbender.test import BenderTestMixin


class TestBend(unittest.TestCase):
    async def test_empty_mapping(self):
        self.assertDictEqual(await bend({}, {'a': 1}), {})

    async def test_flat_mapping(self):
        mapping = {
            'a_field': S('a', 'b'),
            'another_field': K('wow'),
        }
        source = {'a': {'b': 'ok'}}
        expected = {
            'a_field': 'ok',
            'another_field': 'wow',
        }
        self.assertDictEqual(await bend(mapping, source), expected)

    async def test_nested_mapping(self):
        mapping = {
            'a_field': S('a', 'b'),
            'a': {
                'nested': {
                    'field': S('f1', 'f2'),
                },
            },
        }
        source = {
            'a': {'b': 'ok'},
            'f1': {'f2': 'hi'},
        }
        expected = {
            'a_field': 'ok',
            'a': {'nested': {'field': 'hi'}},
        }
        self.assertDictEqual(await bend(mapping, source), expected)

    async def test_nested_mapping_with_lists(self):
        mapping = {
            'a_field': S('a', 'b'),
            'a': [{
                'nested': {
                    'field': S('f1', 'f2'),
                },
            }],
        }
        source = {
            'a': {'b': 'ok'},
            'f1': {'f2': 'hi'},
        }
        expected = {
            'a_field': 'ok',
            'a': [{'nested': {'field': 'hi'}}],
        }
        self.assertDictEqual(await bend(mapping, source), expected)

    async def test_list_with_non_dict_elements(self):
        mapping = {'k': ['foo1', S('bar1')]}
        source = {'bar1': 'val 1'}
        expected = {'k': ['foo1', 'val 1']}
        self.assertDictEqual(await bend(mapping, source), expected)

    async def test_bending_exception_is_raised_when_something_bad_happens(self):
        mapping = {'a': S('nonexistant')}
        source = {}
        with self.assertRaises(BendingException):
            await bend(mapping, source)

    async def test_constants_without_K(self):
        mapping = {'a': 'a const value', 'b': 123}
        self.assertDictEqual(await bend(mapping, {}),
                             {'a': 'a const value', 'b': 123})

    async def test_context_shallow(self):
        mapping = {'a': Context() >> S('b')}
        res = await bend(mapping, {}, context={'b': 23})
        self.assertDictEqual(res, {'a': 23})

    async def test_context_deep(self):
        mapping = {'a': [{'a': Context() >> S('b')}]}
        res = await bend(mapping, {}, context={'b': 23})
        self.assertDictEqual(res, {'a': [{'a': 23}]})


class TestOperators(unittest.TestCase, BenderTestMixin):
    def test_add(self):
        self.assert_bender(K(5) + K(2), None, 7)

    def test_sub(self):
        self.assert_bender(K(5) - K(2), None, 3)

    def test_mul(self):
        self.assert_bender(K(5) * K(2), None, 10)

    def test_div(self):
        self.assert_bender(K(4) / K(2), None, 2)
        self.assertAlmostEqual((K(5) / K(2))(None), 2.5, 2)

    def test_neg(self):
        self.assert_bender(-K(1), None, -1)
        self.assert_bender(-K(-1), None, 1)

    async def test_op_with_context(self):
        mapping = {'res': (Context() >> S('b')) - S('a')}
        in_ = {'a': 23}
        context = {'b': 27}
        res = await bend(mapping, in_, context=context)
        self.assertEqual(res, {'res': 4})

    def test_eq(self):
        self.assert_bender(K(42) == K(42), None, True)
        self.assert_bender(K(42) == K(27), None, False)

    def test_ne(self):
        self.assert_bender(K(42) != K(42), None, False)
        self.assert_bender(K(42) != K(27), None, True)

    def test_and(self):
        self.assert_bender(K(True) & K(True), None, True)
        self.assert_bender(K(True) & K(False), None, False)
        self.assert_bender(K(False) & K(True), None, False)
        self.assert_bender(K(False) & K(False), None, False)

    def test_or(self):
        self.assert_bender(K(True) | K(True), None, True)
        self.assert_bender(K(True) | K(False), None, True)
        self.assert_bender(K(False) | K(True), None, True)
        self.assert_bender(K(False) | K(False), None, False)

    def test_invert(self):
        self.assert_bender(~K(True), None, False)
        self.assert_bender(~K(False), None, True)


class TestGetItem(unittest.TestCase, BenderTestMixin):
    def test_getitem(self):
        bender = S('val')[2:8:2]
        if sys.version_info.major == 2:
            val = range(10)
        else:
            val = list(range(10))
        self.assert_bender(bender, {'val': val}, [2, 4, 6])


if __name__ == '__main__':
    unittest.main()
