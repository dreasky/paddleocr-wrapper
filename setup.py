from setuptools import setup, find_packages

setup(
    name="paddleocr-wrapper",
    version="0.1.5",
    packages=find_packages(include=["paddleocr_wrapper*"]),
    package_data={"paddleocr_wrapper": ["paddleocr_config.json"]},
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "markdownify>=1.2.2",
    ],
    python_requires=">=3.10",
)
