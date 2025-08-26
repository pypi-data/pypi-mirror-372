from setuptools import setup, find_packages
import os
import re

# 读取 README 文件
def read_long_description():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "JetTask - A high-performance distributed task queue system"

# 读取 requirements.txt
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

# 从 pyproject.toml 读取版本号
def read_version():
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            # 查找 version = "x.x.x" 的模式
            match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Warning: Could not read version from pyproject.toml: {e}")
    # 如果读取失败，返回默认版本
    return "0.1.5"

setup(
    name="jettask",
    version=read_version(),
    author="JetTask Team",
    author_email="support@jettask.io",
    description="A high-performance distributed task queue system with web monitoring",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jettask",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jettask=jettask.core.cli:main",
            "jettask-webui=jettask.webui.backend.main:run_server",
            "jettask-monitor=jettask.webui.run_monitor:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jettask": [
            "webui/static/**/*",
            "webui/frontend/dist/**/*",
            "webui/schema.sql",
            "webui/*.html",
        ],
    },
    zip_safe=False,
)