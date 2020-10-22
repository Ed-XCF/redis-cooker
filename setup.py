import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="redis-cooker",
    version="2020.10rc1",
    author="Ed__xu__Ed",
    author_email="m.tofu@qq.com",
    description="An redis operation proxy package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ed-XCF/redis-cooker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache-2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
