from setuptools import setup, find_packages

setup(
    name="json2orm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    description="A simple JSON-based ORM for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sina Firoozan(ReFrameWeb)",
    author_email="sinafiroozan@gmail.com",
    url="https://github.com/OroTeam/json2orm/",
    license="MIT",
    python_requires=">=3.7",
)
