from setuptools import setup
from statblk import version

setup(
    name='statblk',
    version=version,
    description='Gather essential disk and partition info for block devices and print it in a nice table',
    long_description=open('README.txt').read(),
    long_description_content_type='text/plain',
    author='Yufei Pan',
    author_email='pan@zopyr.us',
    url='https://github.com/yufei-pan/statblk',
    py_modules=['statblk'],
    entry_points={
        'console_scripts': [
            'statblk=statblk:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
	license='GPLv3+',
)
