import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kengine-mcp-server",
    version="0.1.2",
    author="Knowledge Engineering Team",
    author_email="your.email@example.com",
    description="MCP (Model Context Protocol) server for knowledge engineering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-organization/knowledge-engineering",
    packages=setuptools.find_packages(include=["mcp_server", "mcp_server.*", "kengine", "kengine.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "langchain>=0.0.267",
        "langchain-core>=0.1.0",
        "numpy>=1.24.0",
        "aiohttp>=3.12.0",
        "anthropic>=0.59.0",
        "faiss-cpu>=1.8.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "langchain-anthropic>=0.3.0",
        "langchain-community>=0.3.0",
        "langchain-openai>=0.2.0",
        "openai>=1.97.0",
        "pydantic>=2.11.0",
        "python-dotenv>=1.1.0",
        "pyyaml>=6.0.0",
        "tiktoken>=0.9.0",
        "pymysql>=1.1.0",
        "dataclasses-json>=0.5.0",
        "boto3<=1.35.99",
    ],
    entry_points={
        "console_scripts": [
            "kengine-mcp-server=mcp_server.__main__:main",
        ],
    },
    include_package_data=True,
)