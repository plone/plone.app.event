from setuptools import setup
from setuptools import find_packages

import os


version = '2.0.dev0'


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
        'icalendar>3.0',
        'plone.app.contentlisting',
        'plone.app.dexterity',
        'plone.app.layout',
        'plone.app.portlets>=2.5a1',
        'plone.app.querystring',
        'plone.app.registry',
        'plone.app.textfield',
        'plone.app.vocabularies',
        'plone.app.widgets [dexterity] >= 1.6.0dev',
        'plone.app.z3cform',
        'plone.autoform>=1.4',
        'plone.behavior',
        'plone.browserlayer',
        'plone.dexterity',
        'plone.event>=1.0',
        'plone.folder',
        'plone.formwidget.recurrence [z3cform]',
        'plone.formwidget.recurrence',
        'plone.indexer',
        'plone.memoize',
        'plone.namedfile',
        'plone.portlets',
        'plone.registry',
        'plone.supermodel',
        'plone.uuid',
        'plone.z3cform',
        'pytz',
        'transaction',
        'z3c.form >= 3.2.1.dev0',
        'zope.annotation',
        'zope.component',
        'zope.container',
        'zope.contentprovider',
        'zope.event',
        'zope.globalrequest',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
    ],
    extras_require={
        'test': [
            'mock',
            'plone.app.collection',
            'plone.app.contenttypes',
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
