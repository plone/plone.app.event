from setuptools import setup, find_packages

version = '1.0dev'

setup(name='plone.app.event',
      version=version,
      description="Event content type for plone",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone event',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://github.com/plone/plone.app.event',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone','plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Acquisition',
          'DateTime',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.DateRecurringIndex',
          'Products.GenericSetup',
          'Zope2',
          'collective.elephantvocabulary',
          'icalendar',
          'plone.app.layout',
          'plone.app.portlets>=2.4.0',
          'plone.app.registry',
          'plone.app.vocabularies',
          'plone.event',
          'plone.formwidget.datetime',
          'plone.formwidget.recurrence',
          'plone.memoize',
          'plone.portlets',
          'plone.registry',
          'plone.uuid',
          'plone.z3cform',
          'pytz',
          'zope.component',
          'zope.contentprovider',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.publisher',
          'zope.schema',
      ],
      extras_require={
          'archetypes': [
              'AccessControl',
              'Products.ATContentTypes',
              'Products.Archetypes',
              'Products.contentmigration',
              'plone.formwidget.datetime [archetypes]',
              'plone.formwidget.recurrence [archetypes]',
              'transaction',
          ],
          'dexterity': [
              'plone.app.dexterity',
              'plone.app.textfield',
              'plone.autoform',
              'plone.behavior',
              'plone.dexterity',
              'plone.formwidget.datetime [z3cform]',
              'plone.formwidget.recurrence [z3cform]',
              'plone.indexer',
              'plone.supermodel',
              'z3c.form',
          ],
          'ploneintegration': [
              'plone.app.event [archetypes]',
              'z3c.unconfigure==1.0.1', # version fix as long as plone depends
                                        # on zope.configuration < 3.8
          ],
          'test': [
              'plone.app.testing',
              'plone.testing',
              'transaction',
              'zope.event',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """)
