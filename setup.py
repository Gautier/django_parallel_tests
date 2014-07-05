"""
"""
from setuptools import setup

setup(
    name='Django parallel tests',
    version='0.0.1',
    long_description=__doc__,
    packages=['parallel_tests'],
    install_requires=["docker-py"],
    include_package_data=True,
    test_suite='parallel_tests.tests',
    zip_safe=False
)
