"""Tests for the reusable date-scoped data cache."""

from pathlib import Path
import tempfile
import time
import unittest

import pandas as pd

from agent.utils.cache import SessionDataCache


class SessionDataCacheTest(unittest.TestCase):
    def test_round_trip_and_copy_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = SessionDataCache(Path(directory), 'test_data', 60)
            key = {'ticker': 'ABC', 'kind': 'prices'}
            original = pd.DataFrame({'Close': [10.0, 11.0]})
            cache.set(key, original)

            cached = cache.get(key)
            pd.testing.assert_frame_equal(cached, original)
            self.assertTrue(list((Path(directory) / 'test_data').glob('*/*.pkl')))
            cached.loc[0, 'Close'] = 0.0
            pd.testing.assert_frame_equal(cache.get(key), original)

    def test_ttl_and_clear(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = SessionDataCache(Path(directory), 'test_expiry', 60)
            cache.set('short-lived', {'value': 1}, ttl=0)
            time.sleep(0.01)
            self.assertIsNone(cache.get('short-lived'))
            cache.set('first', {'value': 1})
            cache.set('second', {'value': 2})
            self.assertEqual(cache.clear(), 3)


if __name__ == '__main__':
    unittest.main()
