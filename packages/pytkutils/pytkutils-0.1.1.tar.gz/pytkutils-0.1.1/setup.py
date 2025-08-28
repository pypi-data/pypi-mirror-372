from setuptools import setup, find_packages

setup(
    name="pytkutils",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pythonnet>=3.0.0,<4.0.0"
    ],
    author="Peter Grønbæk Andersen",
    author_email="peter@grnbk.io",
    description="A Python wrapper for the TK.MSTS.Tokens.dll library by Okrasa Ghia.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "Homepage": "https://github.com/pgroenbaek/pytkutils",
        "Issues": "https://github.com/pgroenbaek/pytkutils/issues",
        "Source": "https://github.com/pgroenbaek/pytkutils",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)