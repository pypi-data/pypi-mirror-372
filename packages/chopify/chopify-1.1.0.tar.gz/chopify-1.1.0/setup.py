from setuptools import setup, find_packages

setup(
    name="chopify",
    version="1.1.0",
    author="Adonis",
    description="Chopify your words.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adondonis/chopify",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
