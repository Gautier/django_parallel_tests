import docker

from django.core.management.base import BaseCommand
from django.conf import settings

from parallel_tests.runner import Runner
from parallel_tests.image_utils import get_requirements


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        required_settings = ["TEST_APPS", "PROJECT_NAME", "REQUIREMENTS"]
        for required_setting in required_settings:
            if not hasattr(settings, required_setting):
                print "Please set the %s settings" % required_setting
                return

        docker_conn = docker.Client(
            base_url='unix://var/run/docker.sock',
            version='1.12',
            timeout=10
        )

        runner = Runner(
            docker_conn,
            settings.PROJECT_NAME,
            requirements=get_requirements(settings.REQUIREMENTS),
            tests=settings.TEST_APPS,
            verbose=False
        )
        return runner.launch_parallel_tests()
