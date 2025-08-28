from setuptools import setup, find_packages

setup(
    name="CICDTest21562",
    version='0.1.0',
    description="A pipeline for diabetes prediction using logistic regression.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "pandas",
        "joblib"
    ],
    python_requires=">=3.7",
)