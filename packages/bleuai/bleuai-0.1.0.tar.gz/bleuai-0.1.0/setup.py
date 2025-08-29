"""
Setup configuration for Bleu AI Python SDK.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bleuai",
    version="0.1.0",
    author="Bleu AI",
    author_email="contact@buildbleu.com",
    description="Python SDK for Bleu AI workflow execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/buildbleu/bleuai-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "httpx>=0.24.0",
        "supabase>=2.0.0",
        "realtime>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ]
    },
    keywords="bleu ai workflow automation api sdk",
    project_urls={
        "Documentation": "https://docs.buildbleu.com",
        "Source": "https://github.com/buildbleu/bleuai-python",
        "Tracker": "https://github.com/buildbleu/bleuai-python/issues",
    },
)
