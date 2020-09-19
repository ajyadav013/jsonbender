from jsonbender.core import Transport


class BenderTestMixin(object):
    async def assert_bender(self, bender, source, expected_value,
                      context=None, msg=None):
        context = context or {}
        got = await bender(Transport(source, context))
        self.assertEqual(got, expected_value, msg)

