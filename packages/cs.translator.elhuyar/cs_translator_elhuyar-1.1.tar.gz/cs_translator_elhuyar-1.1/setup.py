# -*- coding: utf-8 -*-
"""Installer for the cs.translator.elhuyar package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.md").read(),
    ]
)


setup(
    name="cs.translator.elhuyar",
    version="1.1",
    description="An add-on for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Ion Lizarazu",
    author_email="ilizarazu@codesyntax.com",
    url="https://github.com/codesyntax/cs.translator.elhuyar",
    project_urls={
        "PyPI": "https://pypi.org/project/cs.translator.elhuyar/",
        "Source": "https://github.com/codesyntax/cs.translator.elhuyar",
        "Tracker": "https://github.com/codesyntax/cs.translator.elhuyar/issues",
        # 'Documentation': 'https://cs.translator.elhuyar.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["cs", "cs.translator"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "plone.api>=1.8.4",
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
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = cs.translator.elhuyar.locales.update:update_locale
    """,
)
