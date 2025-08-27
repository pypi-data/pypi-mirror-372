# =============================================================================
# 4. setup.py
# =============================================================================

"""
Setup script for swajay-cv-toolkit
"""

from setuptools import setup, find_packages
import os

# Read version
with open("swajay_cv_toolkit/version.py", "r") as f:
    exec(f.read())

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="swajay-cv-toolkit",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swajayresources/swajay-cv-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "examples": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "jupyter>=1.0.0",
            "notebook>=6.0.0",
        ]
    },
    keywords="computer-vision, deep-learning, image-classification, pytorch, machine-learning, neural-networks, augmentation, loss-functions",
    project_urls={
        "Bug Reports": "https://github.com/swajay/swajay-cv-toolkit/issues",
        "Source": "https://github.com/swajay/swajay-cv-toolkit",
        "Documentation": "https://swajay-cv-toolkit.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)