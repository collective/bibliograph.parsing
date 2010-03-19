import os
from setuptools import setup, find_packages

version = '1.0.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('bibliograph', 'parsing', 'README.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' + 
    read('CHANGES.txt')
    )

setup(name='bibliograph.parsing',
      version=version,
      description="Parsers for bibliograph packages",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='bibtex bibliography xml endnote ris bibutils parsers',
      author='Paul Bugni, Cris Ewing',
      author_email='plone-biblio@das-netzwerkteam.de',
      url='http://svn.plone.org/svn/collective/bibliograph.parsing/',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bibliograph'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bibliograph.core',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
