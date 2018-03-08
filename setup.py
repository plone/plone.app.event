from setuptools import setup
from setuptools import find_packages

import os


version = '1.1.12'


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
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
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
        'icalendar>3.0',
        'plone.app.contentlisting',
        'plone.app.form',  # TODO: remove when z3cform portlets are in place
        'plone.app.layout',
        'plone.app.portlets >=2.5.1, <3.0',
        'plone.app.querystring',
        'plone.app.registry',
        'plone.app.vocabularies',
        'plone.browserlayer',
        'plone.event>=1.0',
        'plone.folder',
        'plone.formwidget.datetime>=1.1',
        'plone.formwidget.recurrence >=1.2.1, <2.0dev',
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
        'zope.event',
        'zope.formlib',
        'zope.globalrequest',
        'zope.i18n',
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
            'plone.app.imaging',
            'plone.formwidget.datetime [archetypes]',
            'plone.formwidget.recurrence [archetypes]',
        ],
        'dexterity': [
            'plone.app.dexterity',
            'plone.app.textfield',
            'plone.app.z3cform',
            'plone.autoform>=1.4',
            'plone.behavior',
            'plone.dexterity',
            'plone.formwidget.datetime [z3cform]',
            'plone.formwidget.recurrence [z3cform]',
            'plone.indexer',
            'plone.supermodel',
        ],
        'test': [
            'mock',
            'plone.app.collection',
            'plone.app.contenttypes >= 1.1b1',
            'plone.app.event [archetypes, dexterity]',
            'plone.app.robotframework',
            'plone.app.testing [robot]',
            'plone.testing',
            'robotsuite',
            'transaction',
            'unittest2',
            'zExceptions',
            'zope.event',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
