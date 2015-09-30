#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='galacsian',
      version='1.0.0',
      description='GCS.',
      author='Tim Ryan',
      author_email='tim@3drobotics.com',
      url='https://github.com/3drobotics/galacsian.git',
      install_requires = [
      	'Flask==0.10.1',
      	'protobuf==3.0.0a1',
		'requests==2.5.1',
		'wheel==0.24.0',
    'droneapi==1.5.0',
	  ],
    package_data={
      'galacsian': ['static/images/*', 'static/scripts/*', 'templates/*'],
      },
      entry_points={
          'console_scripts': [
              'galacsian = galacsian.__main__:main'
          ]
      },
      packages=['galacsian'],
      )
