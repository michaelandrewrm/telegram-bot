"""Setup configuration for telegram-notifier package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="telegram-notifier",
    version="1.0.0",
    author="Your Name",
    author_email="michaelandrewrm@example.com",
    description="Easy Telegram notifications for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelandrewrm/telegram-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-telegram-bot>=22.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "isort>=5.0",
        ],
        "full": [
            "python-dotenv>=1.0.0",
            "structlog>=23.0.0",
            "aiofiles>=23.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/michaelandrewrm/telegram-bot/issues",
        "Source": "https://github.com/michaelandrewrm/telegram-bot",
        "Documentation": "https://github.com/michaelandrewrm/telegram-bot/blob/main/README.md#-integration-options",
    },
    keywords="telegram bot notifications messaging alerts monitoring",
    entry_points={
        "console_scripts": [
            "telegram-notify=telegram_notifier.cli:main",
        ],
    },
)
