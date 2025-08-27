#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages, Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Meinolf Sellmann",
    author_email='info@insideopt.com',
    python_requires='>=3.12.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.12',
        'Operating System :: POSIX :: Linux'
    ],
    description="InsideOpt Packaging Line Simulator",
    install_requires=requirements,
    long_description=readme, 
    keywords='insideopt, packaging, demo, optimization',
    name='IOSimulator',
    test_suite='tests',
    version='0.0.8',
    packages=find_packages(include=['IOSimulator', 'IOSimulator.*', '*.so', '*.sio']),
    package_data={'IOSimulator': ['*.so', '*.sio', 'IOSimulator.py']},
    zip_safe=False,
)
