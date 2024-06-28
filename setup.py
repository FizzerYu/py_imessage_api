from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py_imessage_api",
    version="0.1.0",
    author="FizzerYu",
    author_email="changyulve@gmail.com",
    description="A simple Python API to interact with iMessages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FizzerYu/py_imessage_api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
    ],
)