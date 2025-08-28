from setuptools import setup, find_packages

version_file_path = None
version_major = 1
version_minor = 0
version_micro = 0


def get_version():
    res = ["0", "0", "0"]
    res[0] = str(version_major)
    res[1] = str(version_minor)
    res[2] = str(version_micro)
    return ".".join(res)


setup(
    name="qauto_block_test",
    version=get_version(),
    packages=find_packages(),
    description="A simple package that prints hello",
    author="our team",
    author_email="your.email@example.com",
    url="",
    install_requires=[],
    classifiers=['Programming Language :: Python :: 3',],
)
