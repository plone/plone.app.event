from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.app.event',
      version=version,
      description="Event content type for plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone event',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='/svn/plone/plone.app.event/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone','plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Plone',
          'Products.DateRecurringIndex',
          'archetypes.datetimewidget',
          'plone.app.portlets',
          'plone.event',
          'plone.formwidget.recurrence',
          'setuptools',
      ],
      extras_require={
          'test': ['interlude', 'plone.app.testing']
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """)
