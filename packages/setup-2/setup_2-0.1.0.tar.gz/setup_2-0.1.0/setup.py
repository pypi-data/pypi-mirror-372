from setuptools import setup, find_packages

setup(
    name="setup_2",  # package name
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple multi-database connection library (MySQL, MongoDB, SQLite)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/setup_2",  # change if you push to GitHub
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy",
        "pymongo",
        "pymysql"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
