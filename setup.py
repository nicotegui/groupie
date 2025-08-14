from setuptools import setup, find_packages

setup(
    name="groupie",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'gr=groupie.cli:main',
        ],
    },
    python_requires='>=3.7',
    author="Your Name",
    author_email="your.email@example.com",
    description="Virtual file grouper with missing file management",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/groupie",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
