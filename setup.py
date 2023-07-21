from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "5.1.0"


long_description = "\n\n".join(
    [
        Path("README.rst").read_text(),
        (Path(".") / "docs" / "installation.rst").read_text(),
        Path("CHANGES.rst").read_text(),
    ]
)


setup(
    name="plone.app.event",
    version=version,
    description="The Plone calendar framework",
    long_description=long_description,
    long_description_content_type="text/x-rst",
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
    python_requires=">=3.8",
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.base",
        "Products.statusmessages",
        "icalendar",  # >4.0.2
        "Products.DateRecurringIndex",
        "Products.ZCatalog",
        "Products.GenericSetup",
        "plone.app.contenttypes",
        "plone.app.uuid",
        "plone.resource",
        "plone.app.contentlisting",
        "plone.app.dexterity",
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
        "plone.supermodel",
        "plone.uuid",
        "pytz",
        "z3c.form >= 3.2.1",
        "Zope",
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
