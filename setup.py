from setuptools import setup, find_packages

version = '0.1'

setup(name='bibliograph.parsing',
      version=version,
      description="Parsers for bibliograph packages",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='bibtex bibliography xml endnote ris bibutils',
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
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
