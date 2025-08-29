#!/usr/bin/env python
# coding: utf-8

import os
import setuptools
import sys


#: The name of the package on PyPi
PYPI_PACKAGE_NAME = "whatamithinking-pycona"

#: The name of the main Python package
MAIN_PACKAGE_NAME = "pycona"

#: The package URL
PACKAGE_URL = "https://github.com/whatamithinking/pycona"

#: The author email
AUTHOR_EMAIL = "moses.palmer@gmail.com"

#: The runtime requirements
RUNTIME_PACKAGES = ["six"]

#: Additional requirements used during setup
SETUP_PACKAGES = RUNTIME_PACKAGES

#: Packages requires for different environments
EXTRA_PACKAGES = {
    ':sys_platform == "darwin"': ["pyobjc-framework-Quartz >=7.0", "Pillow"],
    ':sys_platform == "linux"': ["python-xlib >=0.17"],
    # xorg. guessing platform name. have not tested.
    ':sys_platform == "arch"': ["Pillow"],
}

PACKAGE_DIR = "whatamithinking"
PACKAGE_DIRPATH = os.path.join(os.path.dirname(__file__), PACKAGE_DIR)


# Read globals from ._info without loading it
INFO = {}
with open(
    os.path.join(
        PACKAGE_DIRPATH, MAIN_PACKAGE_NAME, "_info.py"
    ),
    "rb",
) as f:
    data = f.read().decode("utf-8") if sys.version_info.major >= 3 else f.read()
    code = compile(data, "_info.py", "exec")
    exec(code, {}, INFO)
INFO["author"] = INFO["__author__"]
INFO["version"] = ".".join(str(v) for v in INFO["__version__"])


# Load the read me
try:
    with open(os.path.join(os.path.dirname(__file__), "README.rst"), "rb") as f:
        README = f.read().decode("utf-8")
except IOError:
    README = ""


setuptools.setup(
    name=PYPI_PACKAGE_NAME,
    version=INFO["version"],
    description="Provides systray integration",
    long_description=README,
    long_description_content_type="text/x-rst",
    install_requires=RUNTIME_PACKAGES,
    setup_requires=RUNTIME_PACKAGES + SETUP_PACKAGES,
    extras_require=EXTRA_PACKAGES,
    author=INFO["author"],
    author_email=AUTHOR_EMAIL,
    maintainer="Connor Maynes",
    maintainer_email="connormaynes@gmail.com",
    url=PACKAGE_URL,
    zip_safe=True,
    test_suite="tests",
    license="LGPLv3",
    keywords="system tray icon, systray icon",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 " "(LGPLv3)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows NT/2000",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
)
