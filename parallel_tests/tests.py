from StringIO import StringIO
from mock import patch
from unittest import TestCase
import os
import tarfile

import docker

from parallel_tests.runner import Runner
from parallel_tests.image_utils import create_context

TEST_PROJ = os.path.abspath(__file__ + "/../../test_proj")
REQ = set(('Django==1.6.3',))

class ParallelTestsTestCase(TestCase):
    def setUp(self):
        self.docker = docker.Client(
            base_url='unix://var/run/docker.sock',
            version='1.12',
            timeout=10
        )

    def tearDown(self):
        try:
            self.docker.remove_image(
                "django_parallel_tests/test_proj",
                force=True
            )
        except:
            pass

    def test_create_context(self):
        s = StringIO()
        create_context(["Django"], s)
        s.seek(0)
        context = tarfile.TarFile(fileobj=s)
        names = context.getnames()
        self.assertEqual(len(names), 2)
        self.assertIn("Dockerfile", names)
        self.assertIn("requirements.txt", names)

    def test_name_too_short(self):
        r = Runner(self.docker, "")
        self.assertFalse(r.build_image())

    def test_ok(self):
        r = Runner(self.docker, "test_proj", requirements=REQ)
        self.assertTrue(r.build_image())
        result, = self.docker.images("django_parallel_tests/test_proj")
        self.assertTrue(result["Id"])

    def test_no_requirements(self):
        r = Runner(self.docker, "test_proj")
        r.build_image()

    def test_rebuild_image_once(self):
        r = Runner(self.docker, "test_proj")
        image_name = "django_parallel_tests/test_proj"
        self.assertFalse(self.docker.images(name=image_name))
        r.launch_parallel_tests()
        self.assertTrue(self.docker.images(name=image_name))
        
        with patch.object(Runner, 'build_image') as mock:
            r.launch_parallel_tests()
            self.assertFalse(mock.called)
            self.assertTrue(self.docker.images(name=image_name))

    def test_rebuild_image_when_no_image(self):
        r = Runner(self.docker, "test_proj", requirements=set())
        image_name = "django_parallel_tests/test_proj"
        self.assertFalse(self.docker.images(name=image_name))
        r.launch_parallel_tests()
        self.assertTrue(self.docker.images(name=image_name))
        
        r = Runner(self.docker, "test_proj", requirements=REQ)
        with patch.object(Runner, 'build_image') as mock:
            r.launch_parallel_tests()
            self.assertTrue(mock.called)
