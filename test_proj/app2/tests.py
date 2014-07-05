from django.test import TestCase
import time

class ViewsTest(TestCase):

    def test_slow_app_2(self):
        t0 = time.time()
        time.sleep(5)
        t1 = time.time()
        self.assertTrue(t1 > t0)
