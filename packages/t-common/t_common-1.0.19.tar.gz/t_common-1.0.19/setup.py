from setuptools import setup
import os


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as readme_file_1:
    install_requirements = readme_file_1.readlines()

setup(
    name="t-common",
    packages=[],  # No Python packages, just requirements
    install_requires=install_requirements,
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    description="The package contains all frequently used packages in Thoughtful",
    long_description_content_type="text/x-rst",
    long_description=readme,
    keywords="thoughtful-common-packages, t-common, t_common",
    url="https://www.thoughtful.ai/",
    version="1.0.19",

)
