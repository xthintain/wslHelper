from setuptools import setup, find_packages

setup(
    name="wsl-screenshot-tool",
    version="1.0.0",
    description="WSL Screenshot Tool - Windows screenshot tool with WSL path conversion",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "PyQt5>=5.15.0",
        "Pillow>=10.0.0",
        "mss>=9.0.0",
        "pywin32>=305",
        "pynput>=1.7.6",
        "win10toast>=0.9",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "PyInstaller>=5.13.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "wsl-screenshot=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
)
