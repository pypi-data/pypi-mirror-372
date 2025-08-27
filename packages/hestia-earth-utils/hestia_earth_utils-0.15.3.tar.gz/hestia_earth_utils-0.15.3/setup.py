import pathlib
from setuptools import find_packages, setup

from hestia_earth.utils.version import VERSION

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

REQUIRES = (HERE / 'requirements.txt').read_text().splitlines()

# This call to setup() does all the work
setup(
    name='hestia_earth_utils',
    version=VERSION,
    description="HESTIA's utils library",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/hestia-earth/hestia-utils',
    author='HESTIA Team',
    author_email='guillaumeroyer.mail@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=('tests', 'scripts')),
    include_package_data=True,
    install_requires=REQUIRES,
    python_requires='>=3.9',
    scripts=[
        'bin/hestia-pivot-csv',
        'bin/hestia-format-upload'
    ]
)
