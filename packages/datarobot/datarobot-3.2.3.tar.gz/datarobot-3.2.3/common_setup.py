#
# Copyright 2021-2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import re

DESCRIPTION_TEMPLATE = """
About {package_name}
============================
.. image:: https://img.shields.io/pypi/v/{package_name}.svg
   :target: {pypi_url_target}
.. image:: https://img.shields.io/pypi/pyversions/{package_name}.svg
.. image:: https://img.shields.io/pypi/status/{package_name}.svg

DataRobot is a client library for working with the `DataRobot`_ platform API. {extra_desc}

This package is released under the terms of the DataRobot Tool and Utility Agreement, which
can be found on our `Legal`_ page, along with our privacy policy and more.

Installation
=========================
Python {python_versions} are supported.
You must have a datarobot account.

::

   $ pip install {pip_package_name}

Usage
=========================
The library will look for a config file `~/.config/datarobot/drconfig.yaml` by default.
This is an example of what that config file should look like.

::

   token: your_token
   endpoint: https://app.datarobot.com/api/v2

Alternatively a global client can be set in the code.

::

   import datarobot as dr
   dr.Client(token='your_token', endpoint='https://app.datarobot.com/api/v2')

Alternatively environment variables can be used.

::

   export DATAROBOT_API_TOKEN='your_token'
   export DATAROBOT_ENDPOINT='https://app.datarobot.com/api/v2'

See `documentation`_ for example usage after configuring.

Helpful links
=========================
- `API quickstart guide <https://docs.datarobot.com/en/docs/api/api-quickstart/index.html>`_
- `Code examples <https://docs.datarobot.com/en/docs/api/guide/python/index.html>`_
- `Common use cases <https://docs.datarobot.com/en/docs/api/guide/common-case/index.html>`_

Bug Reporting and Q&A
=========================
Create an account on `DataRobot Community <https://community.datarobot.com/>`_ and post your questions and bug reports
`here <https://community.datarobot.com/t5/forums/postpage/board-id/datarobot-api>`_.

.. _datarobot: https://datarobot.com
.. _documentation: {docs_link}
.. _legal: https://www.datarobot.com/legal/
"""


DEFAULT_CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]


with open("datarobot/_version.py") as fd:
    version_search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE)
    if not version_search:
        raise RuntimeError("Cannot find version information")
    version = version_search.group(1)

if not version:
    raise RuntimeError("Cannot find version information")

_mypy_require = [
    "mypy==1.0.0",
    "types-PyYAML==6.0.12",
    "types-python-dateutil==2.8.19",
    "types-pytz==2022.2.1.0",
    "types-requests==2.28.11",
    "types-urllib3==1.26.25",
]

images_require = ["Pillow==9.2.0"]

lint_require = (
    [
        "black==22.8.0",
        "black[jupyter]==22.8.0",
        "isort==5.10.1",
        "flake8==5.0.4",
        "pylint==2.15.0",
    ]
    + _mypy_require
    + images_require
)

tests_require = [
    "mock==3.0.5",
    "pytest==7.1.2",
    "pytest-cov",
    "responses==0.21",
    "pytest-asyncio",
] + images_require

dev_require = (
    tests_require
    + lint_require
    + images_require
    + [
        "Sphinx==4.3.2",
        "sphinx_rtd_theme==1.0.0",
        "nbsphinx==0.8.9",
        "numpydoc==1.4.0",
        "jupyter_contrib_nbextensions",
        "sphinx-autodoc-typehints==1.17.1",
    ]
)

example_require = [
    "jupyter<=5.0",
    "fredapi==0.4.0",
    "matplotlib>=2.1.0",
    "seaborn<=0.8",
    "scikit-learn<=0.18.2",
    "wordcloud<=1.3.1",
    "colour<=0.1.4",
]

release_require = ["zest.releaser[recommended]==6.22.0"]

# The None-valued kwargs should be updated by the caller
common_setup_kwargs = dict(
    name=None,
    version=None,
    description="This client library is designed to support the DataRobot API.",
    author="datarobot",
    author_email="support@datarobot.com",
    maintainer="datarobot",
    maintainer_email="info@datarobot.com",
    url="https://datarobot.com",
    project_urls={
        "Documentation": "https://datarobot-public-api-client.readthedocs-hosted.com/",
        "Changelog": "https://datarobot-public-api-client.readthedocs-hosted.com/page/CHANGES.html",
        "Bug Reporting": "https://community.datarobot.com/t5/forums/postpage/board-id/datarobot-api",
    },
    license="DataRobot Tool and Utility Agreement",
    packages=None,
    package_data={"datarobot": ["py.typed"]},
    python_requires=">=3.7",
    long_description=None,
    classifiers=None,
    install_requires=[
        "pandas>=0.15",
        "numpy",
        "pyyaml>=3.11",
        "requests>=2.28.1",
        "requests_toolbelt>=0.6",
        "trafaret>=0.7,<2.2,!=1.1.0",
        "urllib3>=1.23",
        "typing-extensions>=4.3.0,<5",
        "mypy-extensions>=0.4.0,<2",
        "strenum>=0.4.15",
    ],
    extras_require={
        "dev": dev_require,
        "examples": example_require,
        "release": release_require,
        "lint": lint_require,
        "images": images_require,
        "test": tests_require,
    },
)
