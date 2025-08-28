"""
Setup configuration for AutoDS Copilot package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="autods-copilot",
    version="0.1.0",
    author="MaheshKumarsg036",
    author_email="contact@autods-copilot.com",
    description="GenAI-powered agent-based tool for automated data science workflows with OpenAI GPT-4o integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MaheshKumarsg036/AutoDS_Copilot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
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
            "mypy>=0.800",
            "pre-commit>=2.15",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "viz": [
            "plotly>=5.0",
            "bokeh>=2.4",
        ]
    },
    entry_points={
        "console_scripts": [
            "autods-copilot=autods_copilot.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "autods_copilot": [
            "config/*.yaml",
            "prompts/templates/*.py",
        ],
    },
    keywords=[
        "data science",
        "machine learning",
        "automated ml",
        "exploratory data analysis",
        "artificial intelligence",
        "agent-based",
        "natural language processing"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/autods-copilot/issues",
        "Source": "https://github.com/your-org/autods-copilot",
        "Documentation": "https://autods-copilot.readthedocs.io/",
    },
)
