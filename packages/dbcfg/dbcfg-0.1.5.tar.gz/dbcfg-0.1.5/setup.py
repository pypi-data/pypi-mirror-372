#!/usr/bin/env python3

import setuptools,distutils,shutil,re,os

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="dbcfg",
    version="0.1.5",
    author="Chen chuan",
    author_email="kcchen@139.com",
    description="数据库连接信息管理",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    zip_safe= False,
    include_package_data = True,
    entry_points={
        'console_scripts':  [
            'dbcfg=script.dbcfgtool:main',
        ],
    },
)
