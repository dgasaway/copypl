from setuptools import setup
import os
import io
from copypl._version import __version__

# Read the long description from the README.
basedir = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(basedir, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='copypl',
    version=__version__,
    description='A Python script for copying files referenced by m3u/m3u8/pls playlists',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='David Gasaway',
    author_email='dave@gasaway.org',
    url='https://bitbucket.org/dgasaway/copypl',
    download_url='https://bitbucket.org/dgasaway/copypl/downloads/',
    license='GNU GPL v2',
    py_modules=['copypl/copypl', 'copypl/_version'],
    entry_points={
        'console_scripts': [
            'copypl = copypl.copypl:main',
        ],
    },
    python_requires='>=3.2',
    keywords='audio music playlist',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Topic :: Multimedia :: Sound/Audio',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
    ],
)
