"""Word to Text MCP Server 包安装配置"""

from setuptools import setup, find_packages
import os

# 读取README文件
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# 读取requirements文件
with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="word-to-txt-mcp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="FastMCP Word文档转文本分析服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/word-to-txt-mcp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/word-to-txt-mcp/issues",
        "Source": "https://github.com/yourusername/word-to-txt-mcp",
        "Documentation": "https://github.com/yourusername/word-to-txt-mcp#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Office/Business :: Office Suites",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "word-to-txt-mcp=word_to_txt_mcp.cli:main",
        ],
    },
    keywords=[
        "mcp", "fastmcp", "word", "document", "text", "analysis", 
        "docx", "conversion", "server", "api"
    ],
    include_package_data=True,
    zip_safe=False,
)