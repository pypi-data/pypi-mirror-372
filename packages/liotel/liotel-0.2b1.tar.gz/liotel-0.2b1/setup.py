from setuptools import setup, find_packages

setup(
    name="liotel",
    version="0.2b1",  # نسخه بتا
    description="A resilient, minimal HTTP client for the Liotel API with retries, caching, and CLI support.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="amiraliali3",
    author_email="amiraliali377.9@gmail.com",
    url="https://github.com/amiraliali3284/liotel",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "liotel=liotel.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",  # حالت بتا
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
)