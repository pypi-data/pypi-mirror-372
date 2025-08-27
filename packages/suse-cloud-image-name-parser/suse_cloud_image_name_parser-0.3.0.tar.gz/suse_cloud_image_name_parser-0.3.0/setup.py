#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Setup script."""

# Copyright (c) 2025 SUSE LLC
#
# This file is part of suse-cloud-image-name-parser
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as req_file:
    requirements = req_file.read().splitlines()

with open('requirements-test.txt') as req_file:
    test_requirements = req_file.read().splitlines()[2:]

with open('requirements-dev.txt') as req_file:
    dev_requirements = test_requirements + req_file.read().splitlines()[2:]


setup(
    name='suse-cloud-image-name-parser',
    version='0.3.0',
    description="Package for SUSE image name data.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="SUSE",
    author_email='public-cloud-dev@susecloud.net',
    url='https://github.com/SUSE-Enceladus/suse-cloud-image-name-parser',
    packages=find_packages(),
    package_dir={
        'suse_cloud_image_name_parser': 'suse_cloud_image_name_parser'
    },
    entry_points={
        'console_scripts': [
        ]
    },
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': test_requirements,
    },
    license='GPLv3+',
    zip_safe=False,
    keywords='suse-cloud-image-name-parser suse_cloud_image_name_parser',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)
