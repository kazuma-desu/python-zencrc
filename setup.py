"""
A command-line tool for CRC32 stuff.
"""
from setuptools import find_packages, setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='zencrc',
    version='0.9.1.1b1',  # PEP440
    url='https://github.com/kazuma-desu/python-zencrc',
    license='GNU GPLv3',
    author='Kavintha Kulasingham',
    author_email='kmuthisha@gmail.com',
    description='ZenCRC command-line tool for CRC32 stuff.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': [
            'zencrc = zencrc.zencrc_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities '
    ]
)
