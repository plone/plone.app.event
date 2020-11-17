# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = '3.2.10'


long_description = ('\n\n'.join([
    open("README.rst").read(),
    open(os.path.join('docs', 'installation.rst')).read(),
    open("CHANGES.rst").read(),
]))


setup(
    name='plone.app.event',
    version=version,
    description="The Plone calendar framework",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords='plone event',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.app.event',
    license='GPL version 2',
    packages=find_packages(),
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
        'icalendar',  # >4.0.2
        'plone.app.contentlisting',
        'plone.app.dexterity',
        'plone.app.layout',
        'plone.app.multilingual',
        'plone.app.portlets >= 2.5.1',
        'plone.app.querystring',
        'plone.app.registry',
        'plone.app.textfield',
        'plone.app.vocabularies >= 2.1.15.dev0',
        'plone.app.z3cform>=2.0.1.dev0',
        'plone.autoform>=1.4',
        'plone.behavior',
        'plone.browserlayer',
        'plone.dexterity',
        'plone.event>=1.0',
        'plone.folder',
        'plone.formwidget.recurrence [z3cform] >= 1.2.4',
        'plone.indexer',
        'plone.memoize',
        'plone.namedfile',
        'plone.portlets',
        'plone.registry',
        'plone.supermodel',
        'plone.uuid',
        'plone.z3cform',
        'pytz',
        'six',
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
        'dexterity': [],  # BBB, remove with next version
        'test': [
            'icalendar >= 3.10',  # otherwise minor test failure
            'mock',
            'plone.app.contenttypes >= 1.2a3',
            'plone.app.robotframework',
            'plone.app.testing [robot]',
            'plone.testing',
            'robotsuite',
            'transaction',
            'zExceptions',
            'zope.event',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
