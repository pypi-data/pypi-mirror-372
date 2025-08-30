from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="calypr_admin",
    version="0.0.1",
    description="A CLI to administer calypr projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="walsbr",
    author_email="walsbr@ohsu.edu",
    url="https://github.com/calypr/admin",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=requirements,
    include_package_data=True,
    package_data={  # Optional
        "": ["*.yaml"],
    },
    entry_points={
        "console_scripts": [
            "calypr_admin=calypr_admin.admin.cli:cli",
        ],
    },
)
