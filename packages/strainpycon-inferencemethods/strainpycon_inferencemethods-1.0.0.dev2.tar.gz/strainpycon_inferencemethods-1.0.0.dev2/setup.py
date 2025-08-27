import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="strainpycon_inferencemethods",
    version="1.0.0.dev2",
    author="Gary Vestal",
    origional_author= "Ymir Vigfusson, Lars Ruthotto, Rebecca M. Mitchell, Lauri Mustonen, Xiangxi Gao",
    author_email="mojihaka@protonmail.com",
    description="Strain disambiguation methods for mixed DNA samples. Built upon strainpycon package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)