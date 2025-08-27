from setuptools import setup, find_packages

setup(
    name="pythontyperlol",  # Pypi name
    version="1.0.0",
    description="A python module i made i guess :D",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Arran Hewitt",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
