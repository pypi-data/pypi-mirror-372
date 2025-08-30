from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yugenkairo-sentinel-sdk",
    version="0.1.1",
    author="Sentinel Team",
    author_email="sentinel-team@example.com",
    description="Python SDK for Sentinel - A self-healing LLM firewall with cryptographic data protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swayam8624/Sentinel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    keywords=["sentinel", "llm", "security", "firewall", "cryptography", "pii", "data-protection"],
    project_urls={
        "Documentation": "https://swayam8624.github.io/Sentinel/",
        "Source": "https://github.com/swayam8624/Sentinel",
        "Tracker": "https://github.com/swayam8624/Sentinel/issues",
    },
)