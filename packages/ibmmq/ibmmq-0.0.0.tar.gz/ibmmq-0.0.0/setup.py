
"""Setup script usable for setuptools."""
#
# Linux build is re-entrant/multithreaded.

# stdlib
import os
import platform

from setuptools import setup

# This is the only place where package version number is set!
# The version should correspond to PEP440 and gets normalised if
# not in the right format. VRM can be followed with a|b|rc with a further numeric
# to indicate alpha/beta/release candidate versions.
version = os.environ.get('PYVER')

long_description = """
This is a placeholder package for now.

"""

_ = setup(name = 'ibmmq',
    version = version,
    description = 'IBM MQ',
    long_description = long_description,
    long_description_content_type = 'text/plain',
    author='IBM MQ Development',
    url='https://ibm.com/software/products/en/ibm-mq',
    platforms='OS Independent',
    package_dir = {'': 'code'},
    packages = ['ibmmq'],
    license='Python-2.0',
    classifiers = [
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
