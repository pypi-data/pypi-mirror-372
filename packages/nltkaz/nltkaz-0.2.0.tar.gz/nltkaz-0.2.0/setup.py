from setuptools import setup, find_packages

setup(
    name="nltkaz",
    version="0.2.0",
    description="A natural language processing toolkit designed for the Azerbaijani language.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="Nagi Nagiyev",
    author_email="nagiyevnagi01@gmail.com",
    packages=find_packages(),
    install_requires=[
        "importlib_resources; python_version<'3.9'"
    ],
    include_package_data=True,
    package_data={
        'nltkaz.stem': ['azwords.txt', 'enwords.txt'],
        'nltkaz.stopwords': ['stopwords.txt']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)