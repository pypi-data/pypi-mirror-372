# setup.py
from setuptools import setup, find_packages

setup(
    name="wtfami",
    version="0.0.0",
    author="地灯dideng",
    author_email="3483434955@qq.com",
    description="A simple library to get the current path.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://pypi.org/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)