#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aosp_easy',  # 包的名字
    author='min',  # 作者
    version='0.2.0',  # 版本号
    license='MIT',

    description='make aosp easy',  # 描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='testmin@outlook.com',  # 你的邮箱**
    url='https://github.com/passion-coder-min/aosp_easy',
    packages=['aosp_easy'],  # 包名
    entry_points={
        'console_scripts': [
            'aosp_easy=aosp_easy.aosp_easy:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)