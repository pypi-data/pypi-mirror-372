from setuptools import setup, find_packages

setup(
  name='nocaps',
  version='0.7.1',
  description='A witty Python code roaster and fixer CLI tool.',
  packages=find_packages(),
  install_requires=[
    "rich",
    "requests",
    "keyring"
  ],
  entry_points={
    "console_scripts":[
      "nocaps=nocaps_cli.nocaps:main"
    ]
  }
)