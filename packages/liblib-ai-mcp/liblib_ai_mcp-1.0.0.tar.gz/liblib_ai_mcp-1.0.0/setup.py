from setuptools import setup, find_packages
import os

# 读取README文件
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "LiblibAI AI图片生成MCP工具 - 支持各种风格的AI图片创作"

# 读取依赖
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
try:
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "mcp>=1.0.0",
        "fastmcp>=0.1.0",
        "requests>=2.25.0",
    ]

setup(
    name="liblib-ai-mcp",
    version="1.0.0",
    author="LiblibAI MCP Developer",
    author_email="developer@example.com",
    description="LiblibAI AI图片生成MCP工具 - 支持各种风格的AI图片创作",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/liblib-ai-mcp",
    project_urls={
        "Homepage": "https://github.com/yourusername/liblib-ai-mcp",
        "Repository": "https://github.com/yourusername/liblib-ai-mcp",
        "Issues": "https://github.com/yourusername/liblib-ai-mcp/issues",
    },
    packages=find_packages(),
    package_data={
        "liblib_ai_mcp": ["*.py"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "liblib-ai-mcp=liblib_ai_mcp.main:main",
        ],
    },
    keywords=["ai", "image-generation", "mcp", "liblib", "artificial-intelligence", "text-to-image"],
    zip_safe=False,
)