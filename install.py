import nltk
import pip

PACKAGES = ["apiclient", "beaker", "bleach", "bottle", "google-api-python-client",
            "httplib2", "nltk", "numpy", "passlib", "pony", "requests", "wikiapi"]

def installPackages():
    for package in PACKAGES:
        pip.main(["install", package])
    nltk.download("averaged_perceptron_tagger")
    nltk.download("punkt")
    nltk.download("universal_tagset")
    #nltk.download("all-nltk")

def uninstallPackages():
    NotImplemented

if __name__ == "__main__":
    installPackages()