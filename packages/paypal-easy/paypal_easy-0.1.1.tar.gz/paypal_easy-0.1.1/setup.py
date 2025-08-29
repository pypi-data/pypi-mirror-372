# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paypal-easy",
    version="0.1.1",
    author="William Mabotja",
    author_email="info@williammabotja.xyz",
    description="A simplified wrapper for PayPal's Python Server SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doculearn/paypal-easy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "paypal-server-sdk>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
        "test": ["pytest>=6.0"]
    },
)
