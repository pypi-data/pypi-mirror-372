from setuptools import setup, find_packages

setup(
    name="cyclic_correlation",
    version="0.1.12",
    description="Cyclic cross-correlation utilities and Zadoff-Chu sequence generation",
    author="Andrea Novero",
    author_email="your@email.com",
    packages=find_packages(),
    install_requires=["numpy"],
    python_requires=">=3.6",
    license="BSD-3-Clause",
    url="https://github.com/noveroandrea/cyclic_correlation", 
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
