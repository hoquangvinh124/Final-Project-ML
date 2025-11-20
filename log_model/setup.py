"""
Setup script for Logistics KPI Prediction System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("deployment/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="logistics-kpi-prediction",
    version="1.0.0",
    author="Data Science Team",
    author_email="support@logistics-ml.com",
    description="ML-based system for predicting logistics KPI scores",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/logistics-kpi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "logistics-api=src.api.app:main",
            "logistics-dashboard=src.dashboard.dashboard:main",
            "logistics-train=src.ml.train_model:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "data/*.csv"],
    },
)
