"""
A command-line tool for CRC32 stuff.
"""
from setuptools import find_packages, setup


setup(
    name='zencrc',
    version='0.8',
    url='https://github.com/kazuma-desu/python-zencrc',
    license='GNU GPLv3',
    author='Kavintha Kulasingham',
    author_email='kmuthisha@gmail.com',
    description='ZenCRC command-line tool for CRC32 stuff.',
    long_description=__doc__,
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
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Operating System :: Unix',
        'Operating System :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities '
    ]
)
