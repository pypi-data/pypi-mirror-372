import unittest

from platform_sdk.helpers.sentry import sentry_ignored, sentry_ignored_urls


class TestSentryIgnored(unittest.TestCase):
    def test_sentry_ignored(self):
        event1 = {"request": {"url": '/up'}}
        event2 = {"request": {"url": '/test.php'}}
        event3 = {"request": {"url": '/not_ignored'}}

        self.assertTrue(sentry_ignored(event1))
        self.assertTrue(sentry_ignored(event2))
        self.assertFalse(sentry_ignored(event3))

    def tests_sentry_ignored_urls(self):
        urls = sentry_ignored_urls()
        self.assertTrue(isinstance(urls, list))
        self.assertTrue(len(urls) > 0)


if __name__ == '__main__':
    unittest.main()
