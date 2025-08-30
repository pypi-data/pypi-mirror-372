from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clickhouse-manager",
    version="0.1.3",
    author="Bogdan Tiyanich",
    author_email="tiyanich.bogdan@gmail.com",
    description="Простой и безопасный интерфейс для работы с ClickHouse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3.0",
        "clickhouse-connect>=0.6.0",
        "clickhouse-driver>=0.2.9"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="clickhouse, database, connector, sql, analytics",
    # Добавляем информацию о возможных проблемах установки
    setup_requires=[
        "wheel",
        "setuptools>=40.8.0"
    ],
)
