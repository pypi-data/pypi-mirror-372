from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='CrumblPy',
    version='1.1.3',
    packages=find_packages(),
    author='Crumbl Data Team',
    author_email='steven.wang@crumbl.com',
    description='Common utility functions for Crumbl Data Team',
    long_description=long_description,  
    long_description_content_type='text/markdown',
    license='Proprietary',
    python_requires='>=3.9',
    install_requires=[
        'boto3>=1.40.19',
        'cryptography>=40.0.2',
        'google_api_python_client>=2.125.0',
        'google-auth-oauthlib>=1.2.0',
        'numpy>=1.26.0',
        'pandas>=2.2.3',
        'prefect>=3.0.3',
        'protobuf>=4.25.5',
        'pyarrow>=17.0.0',
        'slack_sdk>=3.21.3',
        'snowflake-connector-python>=3.15.0'
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-mock>=3.10.0',
        ]
    }
)
