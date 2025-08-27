from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="processss",
    version="0.0.1",
    author="Daniel Sans Reppso da Silva",
    author_email="danielsansrj@gmail.com",
    description="Ferramentas para plotar imagem",
    long_description=page_description,
    long_description_content_type="text/markdown",
    
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)