from setuptools import find_packages
from setuptools import setup

import os


version = "5.0.0"


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open(os.path.join("docs", "installation.rst")).read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="plone.app.event",
    version=version,
    description="The Plone calendar framework",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="plone event",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.app.event",
    license="GPL version 2",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    python_requires=">=3.7",
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.base",
        "ExtensionClass",
        "Products.DateRecurringIndex",
        "Products.statusmessages",
        "icalendar",  # >4.0.2
        "Products.GenericSetup",
        "Products.ZCatalog",
        "persistent",
        "plone.app.contenttypes",
        "plone.app.uuid",
        "plone.resource",
        "zope.annotation",
        "zope.contentprovider",
        "plone.app.contentlisting",
        "plone.app.dexterity",
        "plone.app.layout",
        "plone.app.portlets >= 2.5.1",
        "plone.app.querystring",
        "plone.app.registry",
        "plone.app.textfield",
        "plone.app.vocabularies >= 2.1.15",
        "plone.app.z3cform>=2.0.1",
        "plone.autoform>=1.4",
        "plone.behavior",
        "plone.browserlayer",
        "plone.dexterity",
        "plone.event>=1.0",
        "plone.folder",
        "plone.formwidget.recurrence [z3cform] >= 1.2.4",
        "plone.indexer",
        "plone.memoize",
        "plone.namedfile",
        "plone.portlets",
        "plone.registry",
        "plone.supermodel",
        "plone.uuid",
        "plone.z3cform",
        "pytz",
        "z3c.form >= 3.2.1",
        "zope.globalrequest",
    ],
    extras_require={
        "test": [
            "plone.app.robotframework",
            "plone.app.testing [robot]",
            "plone.testing",
            "robotsuite",
        ],
    },
)
