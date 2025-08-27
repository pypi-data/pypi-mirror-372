from setuptools import setup, find_packages
from pathlib import Path

# Define the root of the project
project_root = Path(__file__).resolve().parent

# Read dependencies and long description
requirements = (project_root / "requirements.txt").read_text().splitlines()
long_description = (project_root / "README.md").read_text()

setup(
    name="clio-manage-api-client",
    version="0.1.4",
    author="Unigrated Partners",
    author_email="dev@unigratedpartners.com",
    description="Python Client for the Clio Manage API.",
    keywords="clio python client, clio api client, clio manage api, legal, client, sdk, integration, unigration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unigrated-solutions/clio-api-python-client",
    project_urls={
        "Bug Tracker": "https://github.com/unigrated-solutions/clio-api-python-client/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
