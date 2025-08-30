from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="guangbo",
    version="0.1.0",
    author="pengmin",
    author_email="877419534@qq.com",
    description="A simple UDP broadcast sender for sending messages to multiple IP addresses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/guangbo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="udp, broadcast, network, messaging",
)