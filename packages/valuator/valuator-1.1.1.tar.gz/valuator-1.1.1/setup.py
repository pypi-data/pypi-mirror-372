from setuptools import setup, find_packages

setup(
    name="valuator",
    version="1.1.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    author="Vikas Konaparthi",
    author_email="vikaskonaparthi@gmail.com",
    description="A lightweight library to fetch and search AI model pricing data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)