from setuptools import setup, find_packages

setup(
    name="dbmini",  # must be unique on PyPI
    version="0.1.2",
    author="Prathamesh Patil ",
    author_email="prathameshpatil0545@gmail.com",
    description="A lightweight DB connector supporting MySQL, SQLite, and MongoDB",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prathamesh9669/dbmini",
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python",
        "pymongo",
        "python-dotenv",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
