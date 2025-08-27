try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import os
import shutil
# copy files into package directory
if os.path.exists("build/lib/vc-utils/conf"):
    shutil.rmtree("build/lib/vc-utils/conf")
shutil.copytree("conf", "build/lib/vc-utils/conf")

setup(
    name="vc-utils",
    version="0.0.4",
    author="Chatavut Viriyasuthee",
    author_email="chatavut@lab.ai",
    description="Vulcan Coalition utililities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vulcan-coalition/vulcan-utils",
    packages=["linkage"],
    package_data={
        "": ["conf/*"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "shortuuid",
        "dotenv",
        "requests"
    ]
)
