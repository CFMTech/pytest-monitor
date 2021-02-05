#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import re
from setuptools import setup, find_packages


def read_version():
    p = pathlib.Path(__file__)
    p = p.parent / 'pytest_monitor' / '__init__.py'
    with p.open('r') as f:
        for line in f:
            if line.startswith('__version__'):
                line = line.split('=')[1].strip()
                match = re.match(r"^['\"](\d+\.\d+\.\d+\w*)['\"]", line)
                if match:
                    return match.group(1)
    raise ValueError('Unable to compute version')


def read(fname):
    file_path = pathlib.Path(__file__).parent / fname
    with file_path.open('r', encoding='utf-8') as f:
        return f.read()


setup(
    name='pytest-monitor',
    version=read_version(),
    author='Jean-Sébastien Dieu',
    author_email='jean-sebastien.dieu@cfm.fr',
    maintainer='Jean-Sébastien Dieu',
    maintainer_email='jean-sebastien.dieu@cfm.fr',
    license='MIT',
    project_urls=dict(Source='https://github.com/CFMTech/pytest-monitor',
                      Tracker='https://github.com/CFMTech/pytest-monitor/issues'),
    url='https://pytest-monitor.readthedocs.io/',
    description='Pytest plugin for analyzing resource usage.',
    long_description=read('README.rst'),
    packages=find_packages('.', exclude=('tests', 'example', 'docs')),
    python_requires='>=3.5',
    install_requires=['pytest', 'requests', 'psutil>=5.1.0', 'memory_profiler>=0.58', 'wheel'],
    options={"bdist_wheel": {"universal": False}},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'monitor = pytest_monitor.pytest_monitor',
        ],
    },
)
