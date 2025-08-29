from setuptools import setup, find_packages

setup(
    name="feature_schema",  
    version="0.1.5",  
    author="Chaaanakyaa Milkuri",
    author_email="chaanakyaam@gmail.com",
    description="A lightweight package to extract, document, and validate feature schemas from pandas DataFrames for ML workflows.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chaanakyaaM/Feature_Schema",  
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "pandas==2.3.2",  
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",  
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
