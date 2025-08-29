#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read()

VERSION = (0, 16, '4a0')

# pragma: no cover
if VERSION[-1] != "final":
    project_version = '.'.join(map(str, VERSION))
else:
    # pragma: no cover
    project_version = '.'.join(map(str, VERSION[:-1]))

setup(
    name="django-psa",
    version=project_version,
    description='Django app for working with '
                'various PSA REST API. Defines '
                'models (tickets, companies, '
                'etc.) and callbacks. ',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords='django connectwise halo autotask rest api python',
    packages=find_packages(),
    author='TopLeft Technologies Ltd.',
    author_email='sam@topleft.team',
    url="https://github.com/topleft-team/django-psa",
    include_package_data=True,
    license='MIT',
    install_requires=[
        'requests',
        'django',
        'setuptools',
        'python-dateutil',
        'retrying',
        'redis',
    ],
    test_suite='runtests.suite',
    tests_require=[
        'names',
        'coverage',
        'flake8',
        'django-test-plus',
        'mock',
        'freezegun',
        'responses',
        'model-mommy',
        'django-coverage',
        'names',
        'django-environ'
    ],
    # Django likes to inspect apps for /migrations directories, and can't if
    # package is installed as an egg. zip_safe=False disables installation as
    # an egg.
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Development Status :: 3 - Alpha',
    ],
)
