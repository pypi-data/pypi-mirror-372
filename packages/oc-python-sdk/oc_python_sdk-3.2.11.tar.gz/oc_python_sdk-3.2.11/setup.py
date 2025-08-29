import os
import re

from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from oc_python_sdk/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version('oc_python_sdk', '__init__.py')

readme = open('README.rst').read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='oc_python_sdk',
    version=version,
    packages=find_packages(exclude='tests'),
    include_package_data=True,
    license='GNU GPLv3 License',
    description='Python SDK',
    long_description=readme,
    url='https://gitlab.com/opencity-labs/area-personale/python_sdk',
    author='Opencontent',
    author_email='emily.lancietti@opencontent.it',
    install_requires=[
        'pydantic~=1.10.2',
        'python-dateutil~=2.8.2',
        'python-dotenv~=0.20.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
    ],
)
