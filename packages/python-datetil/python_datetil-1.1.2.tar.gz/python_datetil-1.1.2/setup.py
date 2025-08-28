from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-datetil", 
    version="1.1.2",
    author="Your Name",
    author_email="your@email.com",
    description="Demo package to simulate typosquatting (for education only)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourgithub/reqeusts-demo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Education",
        "Topic :: Security",
    ],
    python_requires=">=3.6",
)

