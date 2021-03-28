from setuptools import setup, find_packages

import generic

with open("README.md", "r") as readme_file:
    readme = readme_file.read()
    
requirements = ['pyodbc', 'keepercommander']

setup(
      name="generic",
      version=generic.__version__,
      author="Daniel Gallagher",
      author_email="daniel-gallagher@outlook.com",
      description="Generic classes to be re-used for all projects",
      long_description=readme,
      long_description_content_type="text/markdown",
      url="https://github.com/danielgallagher8/generic.git",
      packages=find_packages(),
      install_requires=requirements,
      classifiers=[
              "Programming Language :: Python :: 3.7",
              "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
              ],
      )
