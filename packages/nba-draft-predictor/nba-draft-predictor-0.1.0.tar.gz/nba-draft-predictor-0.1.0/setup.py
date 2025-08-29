from setuptools import setup, find_packages

setup(
    name="nba-draft-predictor",
    version="0.1.0",
    description="NBA Draft Prediction Models and Utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pranav Sathyababu",
    author_email="pranavsathya56@gmail.com",
    url="https://github.com/pranavsat/nba-draft-predictor",
    packages=find_packages(),
    install_requires=[
        "scikit-learn==1.5.1",
        "pandas==2.2.2",
        "joblib==1.4.2",
        "xgboost==2.1.0",
        "hyperopt==0.2.7",
        "lightgbm==4.4.0",
        "lime==0.2.0.1",
        "wandb==0.17.4"
    ],
    python_requires="==3.11.4",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
