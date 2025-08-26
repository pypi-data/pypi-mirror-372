"""
setup.py

This file configures the installation, packaging, and distribution of the `bw-essentials` PyPI project.
It declares metadata, dependencies, and packaging instructions. The package includes reusable Python
utilities for AWS S3, email via SMTP, LakeFS integration, Data Loch, and Microsoft Teams notifications.
"""

from setuptools import setup, find_packages

setup(
    name="bw-essentials-core",
    version="0.1.8",
    author="InvestorAI",
    author_email="support+tech@investorai.in",
    description="Reusable utilities for S3, email, Data Loch, Microsoft Teams Notifications and more.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "boto3~=1.37.30",
        "botocore~=1.37.30",
        "lakefs~=0.9.1",
        "requests~=2.32.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.10",
)
