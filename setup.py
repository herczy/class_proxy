#!/usr/bin/env python

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

import os.path

base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, "README.rst")) as readme_file:
    readme = readme_file.read()

with open(os.path.join(base_path, "HISTORY.rst")) as history_file:
    history = history_file.read().replace(".. :changelog:", "")

setup(
    name="class_proxy",
    version="1.1.0",
    description="class_proxy is a transparent proxy for Python",
    long_description=readme + "\n\n" + history,
    author="Viktor Hercinger",
    author_email="hercinger.viktor@gmail.com",
    url="https://github.com/herczy/class_proxy",
    py_modules=["class_proxy"],
    include_package_data=True,
    license="MIT",
    keywords="class_proxy proxy transparent",
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    test_suite="test_class_proxy",
)
