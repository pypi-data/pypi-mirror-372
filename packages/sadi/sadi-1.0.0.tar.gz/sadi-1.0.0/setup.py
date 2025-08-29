# from ez_setup import use_setuptools
# use_setuptools()

from setuptools import find_packages, setup

setup(
    name="sadi",
    version="0.5.7",
    packages=find_packages(exclude=["test.py", "example.py"]),
    install_requires=[
        "rdflib>=4.0",
        "Werkzeug",
        "webob",
        "python-dateutil",
        "pytidylib",
    ],
    setup_requires=["setuptools"],
    # Python version support
    python_requires=">=3.8",
    # metadata for upload to PyPI
    author="Jamie McCusker",
    author_email="mccusker@gmail.com",
    description="SADI for python.",
    license="New BSD License",
    keywords="Webservices SemanticWeb, RDF, Python, REST",
    url="http://code.google.com/p/sadi/",  # project home page, if any
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
    ],
    # could also include long_description, download_url, classifiers, etc.
)
