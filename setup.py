#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tower-desktop',
      version='1.0.0',
      description='Browser-based GCS.',
      author='Tim Ryan',
      author_email='tim@3drobotics.com',
      url='https://github.com/3drobotics/tower-desktop.git',
      install_requires=[
          'Flask==0.10.1',
          'protobuf==3.0.0a1',
          'requests==2.5.1',
          'wheel==0.24.0',
          'dronekit>=2.0.0b3',
      ],
      package_data={
          'tower': [
              'static/images/*',
              'static/scripts/*',
              'templates/*',
          ],
      },
      entry_points={
          'console_scripts': [
              'galacsian = tower.__main__:main',
              'tower = tower.__main__:main',
          ]
      },
      packages=['tower'])
