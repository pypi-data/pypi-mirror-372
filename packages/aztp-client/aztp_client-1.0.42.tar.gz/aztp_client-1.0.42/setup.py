from setuptools import setup, find_packages

setup(
    name="aztp-client",
    version="1.0.42",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "cryptography>=3.4.0",
        "pydantic>=2.0.0",
    ],
    author="Astha AI",
    author_email="dev@astha.ai",
    description="AZTP (Agentic Zero Trust Protocol) Client Library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/asthaAi/aztp-client",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 