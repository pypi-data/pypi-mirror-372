from setuptools import setup, find_packages

setup(
    name="adaptsapi",
    version="0.1.8",
    author="adapts",
    author_email="dev@adapts.ai",
    description="CLI to enqueue triggers via internal API Gateway → SNS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adaptsai/adaptsapi",    
    license="Adapts API Use-Only License v1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "adaptsapi=adaptsapi.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)