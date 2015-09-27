from setuptools import setup
from setuptools import find_packages

import os


version = '2.0.3'


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
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
    ],
    keywords='plone event',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.app.event',
    license='GPL',
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
        'collective.elephantvocabulary',
        'icalendar > 3.0',
        'plone.app.contentlisting',
        'plone.app.dexterity',
        'plone.app.layout',
        'plone.app.portlets >= 2.5.1',
        'plone.app.querystring',
        'plone.app.registry',
        'plone.app.textfield',
        'plone.app.vocabularies >= 2.1.15.dev0',
        'plone.app.z3cform',
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
        'plone43': [
            'plone.app.widgets [dexterity] >= 1.7.0',
        ],
        'plone50': [  # optional, plone 5 already depends on these versions
            'plone.app.z3cform >= 1.1.0.dev0',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
