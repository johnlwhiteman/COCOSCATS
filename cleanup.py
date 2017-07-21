
import os
import shutil

files=["./Demo/Simple/houseTranslated.html"]
dirs=["./COCOSCATS.egg-info", "./build",
     "./Core/__pycache__", "./Data", "./dist",
     "./Plugin/__pycache__", "./Plugin/Analyzer/__pycache__",
     "./Plugin/IO/__pycache__", "./Plugin/Translator/__pycache__"]

for path in files:
    if os.path.isfile(path):
        os.remove(path)

for path in dirs:
    if os.path.isdir(path):
        shutil.rmtree(path)
