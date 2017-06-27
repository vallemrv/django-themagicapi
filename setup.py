# Run 'setup.py sdist register upload' to upload new version

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-themagicapi',
    version='1.0',
    description='Django application. To launch an api server without endpoint. Create the database on demand',
    long_description=read('README.md'),
    author='Manuel Rodriguez',
    author_email='valle.mrv@gmail.com',
    url='https://github.com/vallemrv/django-themagicapi.git',
    packages=['themagicapi'],
    install_requires=[
          'valleorm',
          'django-tokenapi',
          'django-cors-middleware'
    ],
    license='Apache License, Version 2.0',
)
