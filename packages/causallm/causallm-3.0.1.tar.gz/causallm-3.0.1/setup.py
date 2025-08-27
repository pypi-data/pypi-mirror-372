"""
CausalLLM Open Source Setup
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="causallm",
    version="3.0.1",
    author="CausalLLM Team", 
    author_email="opensource@causallm.com",
    description="Open source causal inference powered by LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rdmurugan/causallm",
    project_urls={
        "Bug Tracker": "https://github.com/rdmurugan/causallm/issues",
        "Documentation": "mailto:durai@infinidatum.net",
        "Enterprise": "mailto:durai@infinidatum.net"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="causal-inference, machine-learning, statistics, llm, artificial-intelligence",
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0", 
        "scikit-learn>=1.0.0",
        "networkx>=2.6.0",
        "scipy>=1.7.0",
        "matplotlib>=3.3.0",
        "plotly>=5.0.0",
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "plugins": [
            "langchain>=0.0.200",
            "llama-index>=0.7.0",
            "transformers>=4.20.0",
            "torch>=1.11.0",
        ],
        "ui": [
            "streamlit>=1.25.0",
            "dash>=2.10.0",
            "gradio>=3.35.0",
        ],
        "full": [
            "langchain>=0.0.200",
            "llama-index>=0.7.0", 
            "transformers>=4.20.0",
            "torch>=1.11.0",
            "streamlit>=1.25.0",
            "dash>=2.10.0",
            "gradio>=3.35.0",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
