from setuptools import setup, find_packages

setup(
    name="tpsms",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",  # For synchronous HTTP requests
        # Add "aiohttp>=3.8.0" if using aiohttp in fetch_cgi_gdpr.py
    ],
    author="Mostafa",
    author_email="himosiiisom@gmail.com",
    description="A Python client for TP-Link router SMS functionality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mosiiisom/tpsms",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)