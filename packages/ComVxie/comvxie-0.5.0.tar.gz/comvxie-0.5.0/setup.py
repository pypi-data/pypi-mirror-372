from setuptools import setup, find_packages

# Read content file README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ComVxie",
    version="0.5.0",
    packges=find_packages(),
    install_requires=[],
    author="Vxie",
    description="Library to consult courses about Hack4u",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
)
