from setuptools import setup, find_packages

setup(
    name="embeddingframework",
    version="1.0.4",
    author="SathishKumar Nagarajan",
    author_email="mail@sathishkumarnagarajan.com",
    description="A high-performance, asynchronous, and extensible Python package for processing files, generating embeddings, and storing them in various vector databases with optional cloud storage integration.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/isathish/embeddingframework",
    packages=find_packages(),
    install_requires=[
        "aiofiles",
        "asyncio",
        "argparse",
        "pytest",
        "pytest-cov"
    ],
    entry_points={
        "console_scripts": [
            "embeddingframework=embeddingframework:main"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
