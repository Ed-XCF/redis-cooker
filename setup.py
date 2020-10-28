import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

with open("version", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="redis-cooker",
    version=version,
    author="Ed__xu__Ed",
    author_email="m.tofu@qq.com",
    description="An redis python datastructures package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ed-XCF/redis-cooker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
)
