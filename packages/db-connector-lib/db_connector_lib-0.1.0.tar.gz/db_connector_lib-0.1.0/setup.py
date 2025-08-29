from setuptools import setup, find_packages

setup(
    name="db-connector-lib",  
    version="0.1.0",
    author="Preeti Latta",
    author_email="preetilatta164@gmail.com",
    description="A simple DB connector for multiple databases",
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python",
        "pymongo"
    ],
    python_requires=">=3.7",
)
