try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vc-utils",
    version="0.0.9",
    author="Chatavut Viriyasuthee",
    author_email="chatavut@lab.ai",
    description="Vulcan Coalition utililities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vulcan-coalition/vulcan-utils",
    packages=["linkage", "vc_config"],
    include_package_data=True,
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
