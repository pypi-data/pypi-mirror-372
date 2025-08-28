# setup.py
from setuptools import setup, find_packages

setup(
    name="scdm-agent",
    version="0.1.0",
    description="Secure Cloud Data Migration Agent (Linux local agent)",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "azure-identity>=1.6.0",
        "azure-storage-blob>=12.11.0",
        "boto3>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "scdm-agent = scdm_agent.cli:main"
        ]
    },
    python_requires=">=3.8",
)

