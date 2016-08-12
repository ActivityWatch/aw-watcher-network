#!/usr/bin/env python

from setuptools import setup

setup(name='aw-watcher-network',
      version='0.1',
      description='ActivityWatch watcher for network',
      author='Måns Magnusson',
      author_email='exoji2e@gmail.com',
      url='https://github.com/ActivityWatch/aw-watcher-network',
      packages=['aw_watcher_network'],
      install_requires=[
          'aw-client',
          'wireless'
      ],
      dependency_links=[
          'https://github.com/ActivityWatch/aw-client/tarball/master#egg=aw-client'
      ],
      entry_points={
          'console_scripts': ['aw-watcher-network = aw_watcher_network:main']
      })
