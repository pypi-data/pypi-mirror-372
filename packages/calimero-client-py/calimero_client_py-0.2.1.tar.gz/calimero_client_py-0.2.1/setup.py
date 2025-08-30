from setuptools import setup, find_packages

setup(
    name="calimero-client-py",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "websockets>=12.0",
        "base58>=2.1.1",
        "pydantic>=2.5.0",
        "aiohttp>=3.9.0",
        "toml>=0.10.2",
        "pynacl>=1.5.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.26.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    author="Calimero Network",
    author_email="support@calimero.network",
    description="Python client SDK for Calimero Network",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/calimero-network/calimero-client-py",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
