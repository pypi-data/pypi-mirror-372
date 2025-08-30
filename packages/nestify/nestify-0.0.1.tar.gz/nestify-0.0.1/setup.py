from setuptools import setup, find_packages

from pathlib import Path
from nestify import __version__ as version

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='nestify',
    version=version,
    keywords=['dict', 'object'],
    description='transform flat key-path dictionaries into nested structures with ease',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT Licence',
    url='https://github.com/Jyonn/nestify',
    author='Jyonn Liu',
    author_email='i@6-79.cn',
    platforms='any',
    packages=find_packages(),
    install_requires=[
    ],
)
