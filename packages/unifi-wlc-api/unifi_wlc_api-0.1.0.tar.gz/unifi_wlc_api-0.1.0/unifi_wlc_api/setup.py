from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="unifi_wlc_api",
    version="0.1.0",
    author="Yue Hui Zhu",
    author_email="your.email@example.com",
    description="Python API client for Ubiquiti UniFi Controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/unifi_wlc_api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
)

