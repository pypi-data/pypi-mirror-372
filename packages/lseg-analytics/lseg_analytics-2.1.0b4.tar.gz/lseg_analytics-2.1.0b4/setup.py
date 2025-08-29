# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
#Carefully change the code below, since stage "merge_to_aaas_python" in py-sdk.gitlab-ci.yml changes the version number by shell command
setup(name="lseg-analytics", 
      version="1.0.0b2",
      packages=find_packages("./src"), 
      python_requires=">=3.8")