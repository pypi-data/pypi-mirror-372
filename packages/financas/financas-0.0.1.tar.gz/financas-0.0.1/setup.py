from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="financas",
    version="0.0.1",
    author="boechat",
    author_email="boechat.andre@gmail.com",
    description="Pequeno estudo de um programa de finanças pessoais",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boechat/package-template/",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)