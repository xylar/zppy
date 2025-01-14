import os
from setuptools import find_packages, setup

# From https://github.com/MPAS-Dev/compass/blob/master/setup.py
def package_files(directory, prefixes, extensions):
    """ based on https://stackoverflow.com/a/36693250/7728169"""
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            parts = filename.split('.')
            prefix = parts[0]
            extension = parts[-1]
            if prefix in prefixes or extension in extensions:
                paths.append(os.path.join('..', path, filename))
    return paths

data_files = package_files('zppy', prefixes=[], extensions=['bash', 'csh', 'ini', 'sh'])

setup(
    name="zppy",
    version="1.0.0rc1",
    author="Ryan Forsyth, Chris Golaz",
    author_email="forsyth2@llnl.gov, golaz1@llnl.gov",
    description="Post-processing software for E3SM",
    python_requires='>=3.6',
    intall_requires=['configobj', 'jinja2'],
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_data={'': data_files},
    entry_points={"console_scripts": ["zppy=zppy.__main__:main"]},
)
