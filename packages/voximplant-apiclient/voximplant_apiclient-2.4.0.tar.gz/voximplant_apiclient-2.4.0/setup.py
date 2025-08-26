import json
import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("../package-config.json", "r") as fc:
    data = json.load(fc)
    package_version = data['version']

setuptools.setup(
    name="voximplant-apiclient",
    version=package_version,
    author="Voximplant",
    author_email="support@voximplant.com",
    description="Voximplant API client library",
    long_description=long_description,
    #    long_description_content_type="text/markdown",
    url="https://voximplant.com/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "pytz",
        "pyjwt",
        "cryptography"
    ]
)
