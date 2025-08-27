from setuptools import setup, find_packages

setup(
    name="pythonipsumlorem", 
    version="0.1.0",
    description="A simple Python module that adds a variable and a Lorem Ipsum function.",
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
