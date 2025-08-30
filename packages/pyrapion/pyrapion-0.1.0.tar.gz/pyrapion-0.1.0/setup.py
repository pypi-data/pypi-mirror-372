#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "requests==2.31.0",
    "pandas==2.2.2",
    "phable==0.1.10",
    "loguru==0.7.2",
    "pytz==2024.1"
]

test_requirements = []

setup(
    author="Long Lê",
    author_email='long.le-van@outlook.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python package for helping restful api interaction",
    entry_points={
        'console_scripts': [
            'pyrapion=pyrapion.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pyrapion',
    name='pyrapion',
    license='MIT',
    packages=find_packages(include=['pyrapion', 'pyrapion.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/longlevan/pyrapion',
    version='0.1.0',
    zip_safe=False,
)
