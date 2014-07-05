import json
from StringIO import StringIO
from functools import partial
from multiprocessing.pool import ThreadPool
#from multiprocessing.pool import Pool
import hashlib
import os
import subprocess
import time

from parallel_tests.image_utils import create_context


state = 0

def run_tests_for_project(project_name, tests):
    global state
    if state == 1:
        return
    current_dir = os.getcwd()
    args = [
        "sudo",
        "docker",
        "run",
        "--sig-proxy=false",
        "--rm=true",
        "-v",
        "%s:/project" % current_dir,
        "django_parallel_tests/%s" % project_name,
        "test",
    ] + tests
    process = subprocess.Popen(args) 

    try:
        while True:
            time.sleep(.1)
            if process.poll() is not None:
                return process.returncode
    except KeyboardInterrupt:
        if process is not None:
            state = 1
            process.terminate()
            process.wait()
    return 1


class Runner(object):

    def __init__(
        self,
        docker,
        project_name,
        requirements=set(),
        tests=[],
        verbose=False
    ):
        self.docker = docker
        self.project_name = project_name
        self.requirements = requirements
        self.tests = tests
        self.verbose = verbose

    def launch_parallel_tests(self):
        image_name = "django_parallel_tests/%s" % self.project_name
        if len(self.docker.images(name=image_name)) == 0:
            self.build_image()

        req_hash = hashlib.sha224(str(sorted(self.requirements))).hexdigest()
        try:
            last_req_hash = open(".last_requirements").read().strip()
        except:
            last_req_hash = None

        if req_hash != last_req_hash:
            self.build_image()
            with open(".last_requirements", "w") as f:
                f.write(req_hash)

        pool = ThreadPool()
        tests = [[test] for test in self.tests]
        run_tests = partial(run_tests_for_project, self.project_name)

        result = pool.map_async(run_tests, tests)
        try:
            while True:
                time.sleep(.1)
                if result.ready():
                    print "got result", result.get()
                    return
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
        else:
            pool.close()
            pool.join()

    def build_image(self):
        if len(self.project_name) < 3:
            return False

        tar_fileobj = StringIO()
        create_context(self.requirements, tar_fileobj)
        tar_fileobj.seek(0)

        success = False
        for chunk in self.docker.build(
            tag="django_parallel_tests/%s" % self.project_name,
            quiet=False,
            fileobj=tar_fileobj,
            custom_context=True,
        ):
            if "Successfully built" in chunk:
                success = True
            if self.verbose:
                print json.loads(chunk)["stream"],
        tar_fileobj.close()

        return success
