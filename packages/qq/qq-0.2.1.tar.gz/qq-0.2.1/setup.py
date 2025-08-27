from setuptools import setup, find_packages

setup(
    name="qq",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "anthropic>=0.18.1",
        "aiohttp>=3.9.3",
        "colorama>=0.4.6",
        "pyperclip>=1.8.2",
        "litellm>=1.0.0",
        "textual>=0.47.0",
        "pywin32>=305; sys_platform == 'win32'"
    ],
    entry_points={
        'console_scripts': [
            'qq=quickquestion.qq:main',
        ],
    },
    author="Southbrucke",
    author_email="qq@southbrucke.com",
    description="A CLI tool for getting quick command-line suggestions using any LLM potentially available",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://southbrucke.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop"
    ],
    python_requires=">=3.6",
    license="Proprietary",
    license_files=("LICENSE",),
)