"""
Setup for cloakrt package
Competition-ready package for OpenAI GPT-OSS-20B Red-Teaming
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="cloakrt",
    version="0.1.0",
    author="Adam Hartman",
    description="Framing-first red-teaming for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hartmantexas/cloakrt",
    packages=["cloakrt", "cloakrt.probes", "cloakrt.tests"],
    package_dir={"cloakrt": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ]
    },
    entry_points={
        "console_scripts": [
            "cloakrt=cloakrt.cli:main",
        ],
    },
    package_data={
        "cloakrt": [
            "schemas/*.json",
            "grids/*.yaml",
            "templates/*.txt",
        ],
    },
    include_package_data=True,
)