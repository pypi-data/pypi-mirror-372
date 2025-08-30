import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "tm-cdk-constructs",
    "version": "0.0.51",
    "description": "A CDK construct library",
    "license": "GPL-3.0-or-later",
    "url": "https://github.com/toumoro/cdk-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Toumoro ",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/toumoro/cdk-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "tm-cdk-constructs",
        "tm-cdk-constructs._jsii"
    ],
    "package_data": {
        "tm-cdk-constructs._jsii": [
            "tm-cdk-constructs@0.0.51.jsii.tgz"
        ],
        "tm-cdk-constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.188.0, <3.0.0",
        "cdk-nag>=2.35.66, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.111.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
