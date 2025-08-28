#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

def get_version():
    import re
    version_file = "sagea/_version.py"
    with open(version_file, "r", encoding="utf-8") as f:
        version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Package meta-data.
NAME = 'sagea'
DESCRIPTION = 'satellite gravity post-processing and error assessment'
URL = 'https://github.com/LiuSH1997/sageaPyPI'
EMAIL = 'liushuhao@hust.edu.cn'
AUTHOR = 'Shuhao Liu'
REQUIRES_PYTHON = '>=3.9.0'
VERSION = get_version()
print(VERSION)

# What packages are required for this module to be executed?
REQUIRED = [
    # "numpy~=2.0.2",
    # "scipy==1.13.1",
    # "h5py==3.14.0",
    # "pandas==2.3.0",
    # "tqdm==4.67.1",
    # "netCDF4==1.7.2",
    # "geopandas==1.0.1",
    # "shapely==2.0.7",
    # "pyproj==3.6.1",
    # "rasterio==1.4.3",
    # "cartopy==0.23.0",
    # "wget==3.2",
    "numpy",
    "scipy",
    "h5py",
    "pandas",
    "tqdm",
    "netCDF4",
    "geopandas",
    "shapely",
    "pyproj",
    "rasterio",
    "cartopy",
    "wget",
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# Non-code files
package_data = {
    'sagea': [
        '__data__/auxiliary/GIF48.gfc',
        '__data__/auxiliary/ocean360_grndline.sh',
        '__data__/Geometric/*.nc',
        '__data__/LoveNumber/LoveNumber.mat',
    ]
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    package_data=package_data,

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
