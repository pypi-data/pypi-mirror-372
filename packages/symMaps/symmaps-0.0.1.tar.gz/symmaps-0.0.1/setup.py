import setuptools

with open("README.md", "r") as file:
  long_description = file.read()

setuptools.setup(
  name="symMaps",
  version="0.0.1",
  author="Rasmus K. Skjødt Berg",
  author_email="rasmus.kehlet.berg@econ.ku.dk",
  description="System of mappings to navigate stacked system of equations defined over pandas indices",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ChampionApe/symMaps",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
  ],
  python_requires='>=3.11',
  install_requires=["pandas", "scipy","pyDbs"],
)