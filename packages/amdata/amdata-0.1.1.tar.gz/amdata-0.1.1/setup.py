from setuptools import setup, find_packages

setup(
    name='amdata',
    version='0.1.1',
    description='A simple and easy-to-use library to manage SQLite databases.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Amjad',
    author_email='amjadchoufi@gmail.com',
    url='https://github.com/HACKER-AMJAD',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    install_requires=[],
    python_requires='>=3.6',
)
