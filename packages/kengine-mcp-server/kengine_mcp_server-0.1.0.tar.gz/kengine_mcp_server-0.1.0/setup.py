import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kengine-mcp-server",
    version="0.1.0",
    author="Knowledge Engineering Team",
    author_email="your.email@example.com",
    description="MCP (Model Context Protocol) server for knowledge engineering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-organization/knowledge-engineering",
    packages=setuptools.find_packages(include=["mcp_server", "mcp_server.*"]),
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
    ],
    entry_points={
        "console_scripts": [
            "kengine-mcp-server=mcp_server.__main__:main",
        ],
    },
    include_package_data=True,
)