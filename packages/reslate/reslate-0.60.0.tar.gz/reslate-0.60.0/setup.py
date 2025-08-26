import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


REQUIRES = [
    "pyyaml",
]

EXTRAS = {
    "dev": ["black", "pre-commit",],
}

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Documentation",
    "Topic :: Documentation",
    "Topic :: Documentation :: Sphinx",
]

KEYWORDS = "documentation api automated"

setup(
    name="reslate",
    use_scm_version={"write_to": "reslate/version.py"},
    author="Samuel Rowlinson",
    author_email="sjrowlinson@virginmedia.com",
    description=(
        "A command-line tool to automate generation of neatly-formatted Sphinx-based API documentation pages."
    ),
    url="https://gitlab.com/ifosim/finesse/reslate",
    license="GPL",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=REQUIRES,
    setup_requires=["setuptools_scm"],
    extras_require=EXTRAS,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    project_urls={"Source": "https://gitlab.com/ifosim/finesse/reslate",},
    package_data={"reslate": ["templates/templates/*.rst",]},
    include_package_data=True,
    entry_points={"console_scripts": ["reslate = reslate.__main__:main"]},
)
