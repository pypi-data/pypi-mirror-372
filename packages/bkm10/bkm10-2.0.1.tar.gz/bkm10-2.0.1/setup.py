"""
Entry point for installing the package.
"""

# Native Library | setuptools
from setuptools import setup, find_packages

# (1): Use setup() to... set up the package:
setup(
    name = "bkm10_lib",
    version = "2.0.1",
    description = "A Python library to help nuclear physicists use the BKM formalism in predicting cross-section, asymmetries, and comparing GPD models.",
    author = "Woofmagic",
    author_email = "none@none.none",
    url = "https://github.com/Woofmagic/bkm10_lib",
    project_urls = {
        "Sources": "https://github.com/Woofmagic/bkm10_lib",
        "Bug Tracker": "https://github.com/Woofmagic/bkm10_lib/issues",
        'Changelog': 'https://github.com/Woofmagic/bkm10_lib/CHANGELOG.rst',
    },
    packages = find_packages(),
    classifiers = [
        # (X): For the complete classifier list, visit: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha', # There are 7 of these --- make sure you know which one is correct!
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Physics',
        'Natural Language :: English'
    ],
    keywords = [
        'Physics', 
        'Nuclear Physics', 
        'Particle Physics',
        'Hadronic Physics',
        'Form Factors',
        'Parton Distributions',
        'Parton Distribution Functions',
        'Generalized Parton Distributions',
        'NumPy',
        'Pandas',
        'TensorFlow',
        'Mathematics',
    ],
    python_requires = '>=3.7',
)
