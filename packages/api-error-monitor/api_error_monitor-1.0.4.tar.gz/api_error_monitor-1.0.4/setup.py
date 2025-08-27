import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = [
    'requests>=2.20.0',
]

setuptools.setup(
    name="api_error_monitor",
    version="1.0.4",
    author="Davis Smith",
    author_email="daviss@bucknerheavylift.com",
    description="A Python package for consistent API error monitoring and tracking.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BucknerHeavyLiftCranes/api_error",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=install_requires,
    include_package_data=True,
)