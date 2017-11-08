#
#  Copyright 2016-present, Apstra, Inc.  All rights reserved.
#
#  This source code is licensed under Community End User License Agreement
#  found in the LICENSE.txt file in the root directory of this source tree.
#

from setuptools import setup, find_packages
from glob import glob
from os import path


def requirements(filename):
    return filter(None, [
        line.strip()
        for line in open(filename).readlines()])


libdir = 'pylib'
aeondir = 'pylib/aeon'
packages = find_packages(libdir)

setup(
    name="aeon-venos",
    version="0.9.5",
    author="Jeremy Schulman",
    url='https://github.com/Apstra/aeon-venos',
    author_email="jeremy@apstra.com",
    description="Aeon vendor NOS driver library",
    license="Apache 2.0",
    keywords="networking automation vendor-agnostic",
    package_dir={'': libdir},
    packages=packages,
    extras_require={
        "eos": ["pyeapi", "pexpect==4.2.1"],
        "nxos": ["lxml", "requests", "pexpect==4.2.1"],
        "cumulus": ["paramiko<2.0.0", "pexpect==4.2.1"],
        "ubuntu": ["paramiko<2.0.0", "pexpect==4.2.1"],
        "centos": ["paramiko<2.0.0", "pexpect==4.2.1"]
    },
    scripts=glob('bin/*'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
