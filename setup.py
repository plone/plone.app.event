from setuptools import setup
from setuptools import find_packages

import os


version = '1.0.4'


setup(
    name='plone.app.event',
    version=version,
    description="The Plone calendar framework",
    long_description="%s%s%s%s" % (
        open("README.rst").read() + "\n",
        open(os.path.join('docs', 'installation.rst')).read() + "\n",
        open(os.path.join('docs', 'contributors.rst')).read() + '\n',
        open("CHANGES.rst").read(),
    ),
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
    namespace_packages=['plone', 'plone.app'],
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
        'Products.ZCatalog',
        'Products.statusmessages',
        'Zope2',
        'collective.elephantvocabulary',
        'icalendar',
        'plone.app.contentlisting',
        'plone.app.imaging',
        'plone.app.layout',
        'plone.app.portlets>=2.4.0',
        'plone.app.registry',
        'plone.app.vocabularies',
        'plone.browserlayer',
        'plone.event>=1.0',
        'plone.formwidget.datetime',
        'plone.formwidget.recurrence',
        'plone.formwidget.namedfile',
        'plone.memoize',
        'plone.namedfile',
        'plone.portlets',
        'plone.registry',
        'plone.uuid',
        'plone.z3cform',
        'pytz',
        'transaction',
        'z3c.form',
        'zope.annotation',
        'zope.component',
        'zope.container',
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
        ],
        'dexterity': [
            'plone.app.dexterity',
            'plone.app.textfield',
            'plone.autoform>=1.4',
            'plone.behavior',
            'plone.dexterity',
            'plone.formwidget.datetime [z3cform]',
            'plone.formwidget.recurrence [z3cform]',
            'plone.indexer',
            'plone.supermodel',
        ],
        'ploneintegration': [
            'plone.app.event [archetypes]',
            'z3c.unconfigure',
        ],
        'test': [
            'mock',
            'plone.app.collection',
            'plone.app.contenttypes',
            'plone.app.event [archetypes, dexterity, ploneintegration]',
            'plone.app.testing',
            'plone.testing',
            'transaction',
            'zope.event',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
