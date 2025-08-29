from setuptools import setup, find_packages

readme = ""
with open("README.md") as rf:
    readme = rf.read()

setup(
    name="totvs_dta_utils",
    author="TOTVS - IDEIA",
    version="1.4.3",
    author_email="info@totvs.ai",
    python_requires=">=3.10",
    description="Lib for integration with DTA services",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=[],
    packages=find_packages(include=["dta_utils_python", "dta_utils_python.*"]),
    url="https://github.com/totvs-ai/dta-utils-python",
    extras_require={
        "secrets": [
            "python-dotenv>=1.0.0",
            "requests>=2.0.0"
        ],
        "apikeys": [
            "python-dotenv>=1.0.0",
            "requests>=2.0.0"
        ],
    },
)
