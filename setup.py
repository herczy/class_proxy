#!/usr/bin/env python

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup


setup(
    name="class_proxy",
    version="1.0.0",
    description="Class proxy",
    long_description="Class proxy",
    author="Viktor Hercinger",
    author_email="hercinger.viktor@gmail.com",
    py_modules=["class_proxy"],
    zip_safe=False,
)
