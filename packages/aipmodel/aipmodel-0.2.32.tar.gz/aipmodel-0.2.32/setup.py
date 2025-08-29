import os

from setuptools import find_packages, setup


def read_meta():
    here = os.path.abspath(os.path.dirname(__file__))
    version = None
    description = None
    with open(os.path.join(here, "aipmodel", "__init__.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"')
            elif line.startswith("__description__"):
                description = line.split("=")[1].strip().strip('"')
    return version, description


version, description = read_meta()

setup(
    name="aipmodel",
    version="0.2.32",
    description=description,
    author="AIP MLOPS Team",
    author_email="mohmmadweb@gmail.com",
    url="https://github.com/AIP-MLOPS/model-registry",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.40.11",
        "clearml>=2.0.2",
        "python-dotenv>=1.1.1",
        "requests>=2.32.4",
        "huggingface-hub>=0.34.4",
        "tqdm>=4.67.1",
        "tabulate>=0.9.0",
    ],
    python_requires=">=3.6",
)