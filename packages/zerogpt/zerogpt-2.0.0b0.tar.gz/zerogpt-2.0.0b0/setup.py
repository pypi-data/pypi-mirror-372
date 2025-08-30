from setuptools import setup, find_packages

# Читаем содержимое README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zerogpt",
    version="2.0.0b0",
    author="Redpiar",
    author_email="Regeonwix@gmail.com",
    maintainer="Redpiar",
    maintainer_email="Regeonwix@gmail.com",
    description="Python client for interacting with the ZeroGPT API and generating images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    license_files=["LICENSE"],
    url="https://github.com/RedPiarOfficial/ZeroGPT",
    project_urls={
        "Homepage": "https://github.com/RedPiarOfficial/ZeroGPT",
        "Documentation": "https://red-3.gitbook.io/zerogpt/",
        "Repository": "https://github.com/RedPiarOfficial/ZeroGPT",
        "Bug Tracker": "https://github.com/RedPiarOfficial/ZeroGPT/issues",
    },
    packages=find_packages(include=["zerogpt*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "httpx",
        "httpx[http2]",
        "fake_useragent",
        "pandas",
        "requests_toolbelt",
        "packaging",
        "urlextract",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
    },
    keywords=[
        "ai", "zerogpt", "arting", "text", "image", 
        "free", "api", "uncensured", "gpt", "deepseek", "chatgpt"
    ],
    include_package_data=True,
    package_data={
        "*": ["*.txt", "*.md", "*.rst"]
    },
) 