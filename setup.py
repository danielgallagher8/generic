from setuptools import setup, find_packages

import generic

with open("README.md", "r") as readme_file:
    readme = readme_file.read()
    
requirements = []

setup(
      name="generic",
      version=generic.__version__,
      author="Daniel Gallagher",
      author_email="daniel-gallagher@outlook.com",
      description="Generic classes to be re-used for all projects",
      long_description=readme,
      long_description_content_type="text/markdown",
      url="",
      packages=find_packages(),
      install_requires=requirements,
      classifiers=[
              "Programming Language :: Python :: 3.7",
              "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
              ],
      )
