from setuptools import setup, find_packages

setup(
    name="openworlds",
    version="0.1.0",
    description="Open Worlds: A Python package for creating and managing open-world environments.",
    author="Filip Djurdjevic",
    author_email="filipdj98@gmail.com",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    url="https://github.com/openworlds-ai/openworlds-main",
    license="Apache-2.0",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
