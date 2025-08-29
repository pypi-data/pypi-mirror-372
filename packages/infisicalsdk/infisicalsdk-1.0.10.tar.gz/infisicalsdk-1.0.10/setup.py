# coding: utf-8

"""
    Infisical SDK

    List of all available APIs that can be consumed
"""  # noqa: E501

from setuptools import setup, find_packages  # noqa: H301

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools
NAME = "infisicalsdk"
VERSION = "1.0.10"
PYTHON_REQUIRES = ">=3.8"
REQUIRES = [
    "python-dateutil",
    "aenum",
    "requests~=2.32",
    "boto3~=1.35",
    "botocore~=1.35",
]

setup(
    name=NAME,
    version=VERSION,
    description="Infisical API Client",
    author="Infisical",
    author_email="support@infisical.com",
    url="https://github.com/Infisical/python-sdk-official",
    keywords=["Infisical", "Infisical API", "Infisical SDK"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description_content_type='text/markdown',
    long_description="""\
    Infisical SDK client for Python. To view documentation, please visit https://github.com/Infisical/python-sdk-official
    """,  # noqa: E501
    package_data={"infisicalapi_client": ["py.typed"]},
)
