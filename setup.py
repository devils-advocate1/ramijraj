from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ethicaldrm",
    version="1.0.0",
    author="Ramij Raj",
    author_email="ramijraj31@gmail.com",
    description="A lightweight content protection toolkit for independent creators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devils-advocate1/ethicaldrm",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "cryptography>=3.4.0",
        "pyjwt>=2.0.0",
        "requests>=2.25.0",
        "opencv-python>=4.5.0",
        "imagehash>=4.2.0",
        "psutil>=5.8.0",
        "telethon>=1.24.0",
        "beautifulsoup4>=4.9.0",
        "ffmpeg-python>=0.2.0",
        "click>=8.0.0",
        "watchdog>=2.1.0",
        "numpy>=1.21.0",
        "pillow>=8.0.0",
    ],
    extras_require={
        "ai": ["tensorflow>=2.6.0", "torch>=1.9.0"],
        "dev": ["pytest>=6.0.0", "black>=21.0.0", "flake8>=3.9.0"],
    },
    entry_points={
        "console_scripts": [
            "ethicaldrm=ethicaldrm.cli:main",
            "ethicaldrm-api=ethicaldrm.api.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ethicaldrm": ["templates/*", "static/*"],
    },
)