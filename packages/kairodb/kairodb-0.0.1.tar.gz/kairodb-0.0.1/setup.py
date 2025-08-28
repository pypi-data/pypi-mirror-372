from setuptools import setup, find_packages

setup(
    name="kairodb",  # <-- reserve this name on PyPI
    version="0.0.1",
    author="Your Name",
    author_email="hello@kairodb.com",
    description="KairoDB Python SDK (placeholder)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kairodb/kairodb",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: PostgreSQL License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
