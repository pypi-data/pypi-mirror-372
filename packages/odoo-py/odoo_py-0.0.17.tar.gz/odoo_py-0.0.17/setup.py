from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="odoo-py",
    version="0.0.17",
    author="Rafael Galleani",
    description="Interface to call Odoo API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IT-NOSSA-FARMACIA/odoo-py",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    dependency_links=[],
)
