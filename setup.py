from setuptools import setup, find_packages
import os

version = '1.0a1'

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
          'setuptools',
          'icalendar',
          'plone.event', # evaluate if that will still be needed

          # TODO: re-list dependencies
          # -*- Extra requirements: -*-
          'Acquisition',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.DateRecurringIndex',
          'Products.PloneTestCase',
          'Zope2',
          'collective.elephantvocabulary',
          'icalendar',
          'plone.app.layout',
          'plone.app.portlets',
          'plone.app.registry',
          'plone.formwidget.recurrence',
          'plone.memoize',
          'plone.portlets',
          'plone.registry',
          'plone.z3cform',
          'zope.component',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
      ],
      extras_require={
          'archetypes': [
              'DateTime',
              'Products.Archetypes',
              'Products.ATContentTypes',
              'plone.formwidget.datetime [archetypes]',
          ],
          'dexterity': [
              'plone.behavior',
              'plone.directives.form',
              'plone.formwidget.datetime [z3cform]',
              'five.grok',
              'plone.app.dexterity',
              #'plone.dexterity',
              'zope.schema',
              'zope.interface',
              'zope.component',
          ],
          'test': [
              #'interlude',
              'plone.testing',
              'plone.app.testing',
              'zope.annotation',
              'transaction',
              'zope.site',
              'Products.GenericSetup',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """)
