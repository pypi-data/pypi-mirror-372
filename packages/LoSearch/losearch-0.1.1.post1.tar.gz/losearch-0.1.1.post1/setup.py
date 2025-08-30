
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="LoSearch",
    version="0.1.1.post1",
    author="Madric",
    author_email="madric.offical@gmail.com",
    description="A high-performance Python search library with intelligent relevance scoring, advanced indexing capabilities, and multilingual support for Persian and English.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MadricTeam/LoSearch",
    packages=find_packages(where="losearch"),
    package_dir={"": "losearch"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    install_requires=[
    'build>=1.2.2',
    'flask>=3.0.3',
    'nltk>=3.9.1',
    'redis>=6.1.1',
    'scikit-learn>=1.3.2',
    'sqlalchemy>=2.0.0',
    ],

    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
    keywords="search, indexing, text-processing, multilingual, persian, farsi",
    project_urls={
        "Bug Reports": "https://github.com/MadricTeam/LoSearch/issues",
        "Source": "https://github.com/MadricTeam/LoSearch",
        "Documentation": "https://github.com/MadricTeam/LoSearch/blob/main/LoSearch_Tutorial.md",
    },
)
