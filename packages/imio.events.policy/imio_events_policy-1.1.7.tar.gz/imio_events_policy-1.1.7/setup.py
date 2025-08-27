# -*- coding: utf-8 -*-
"""Installer for the imio.events.policy package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="imio.events.policy",
    version="1.1.7",
    description="Policies to setup imio.events",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Christophe Boulanger",
    author_email="christophe.boulanger@imio.be",
    url="https://github.com/imio/imio.events.policy",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/imio.events.policy",
        "Source": "https://github.com/imio/imio.events.policy",
        "Tracker": "https://github.com/imio/imio.events.policy/issues",
        # 'Documentation': 'https://imio.events.policy.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["imio", "imio.events"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "z3c.jbot",
        "plone.api>=1.8.4",
        "plone.restapi",
        "plone.app.dexterity",
        "collective.autopublishing",
        "collective.big.bang",
        "collective.js.jqueryui",  # TODO : plone6 : remove
        "collective.messagesviewlet",
        "collective.solr",
        "collective.z3cform.select2",
        "eea.facetednavigation",
        "pas.plugins.imio",
        "pas.plugins.kimug",
        "imio.gdpr",
        "imio.events.core",
        "imio.smartweb.locales",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
        ],
    },
    entry_points="""""",
)
