""" pygmail """
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    README = f.read()

requires = [
    "cachetools",
    "certifi",
    "charset-normalizer",
    "google-api-core",
    "google-api-python-client",
    "google-auth",
    "google-auth-httplib2",
    "google-auth-oauthlib",
    "googleapis-common-protos",
    "httplib2",
    "idna",
    "oauthlib",
    "protobuf",
    "pyasn1",
    "pyasn1-modules",
    "pyparsing",
    "pytest",
    "requests",
    "requests-oauthlib",
    "rsa",
    "six",
    "uritemplate",
    "urllib3",
]

setup(
    name="pygmail",
    version=0.1,
    description="Python GMail API Wrapper",
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: IMAP",
    ],
    keywords="Mail API Google",
    author="admin",
    author_email="mike@skelton.onl",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    # entry_points="""\
    #  [paste.app_factory]
    # main=bitomb:main
    # """,
    # paster_plugins=["pyramid"],
)
