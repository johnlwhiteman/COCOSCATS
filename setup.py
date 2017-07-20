import nltk
from setuptools import setup

setup(
    name = "COCOSCATS",
    packages = ["Core", "Plugin"],
    version = "1.0.0",
    description = "A Grammar-Free Natural Language Learning Content Generation and Insertion Framework",
    long_description = "This is a semi-automated framework that generates contextually correct content for people teaching/learning a second language.",
    author = "John L. Whiteman",
    author_email = "Foo@foofoo.com",
    url = "https://github.com/johnlwhiteman/COCOSCATS",
    download_url = "https://github.com/johnlwhiteman/COCOSCATS",
    license = "BSD 3-clause \"New\" or \"Revised\" License",
    keywords = ["language", "grammar-free", "contextual"],
    platforms = "Any that supports Anaconda Python >= 3.0",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: BSD 3-clause \"New\" or \"Revised\" License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Natural Language :: English",
        "Natural Language :: Indonesian",
        "Topic :: Education",
        "Topic :: Text Processing"
    ],
    install_requires = ["BingTranslator", "bottle", "nltk", "numpy", "pony", "wikiapi"],
    package_data = {"":["README.md"]}
)
nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")
nltk.download("universal_tagset")
#nltk.download("all-nltk")