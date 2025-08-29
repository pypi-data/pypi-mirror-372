from setuptools import setup, find_packages

setup(
    name="mbxai",
    version="2.0.3",
    author="MBX AI",
    description="MBX AI SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.12",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.9.1",
        "fastapi>=0.115.12",
        "mcp>=1.7.1",
        "openai>=1.77.0",
        "python-multipart>=0.0.20",
        "sse-starlette>=2.3.4",
        "starlette>=0.46.2",
        "uvicorn>=0.34.2",
        "pydantic-settings>=2.9.1"
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-asyncio>=0.26.0",
            "pytest-cov>=6.1.1",
            "black>=24.3.0",
            "isort>=5.13.2",
            "mypy>=1.8.0"
        ]
    },
    project_urls={
        "Homepage": "https://www.mibexx.de",
        "Documentation": "https://www.mibexx.de",
        "Repository": "https://gitlab.com/mbxai/mbxai-sdk.git"
    }
) 