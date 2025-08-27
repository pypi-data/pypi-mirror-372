# pyMaBoSS

[![PyPI version](https://badge.fury.io/py/maboss.svg)](https://badge.fury.io/py/maboss)
[![Anaconda-Server Badge](https://anaconda.org/colomoto/pymaboss/badges/version.svg)](https://anaconda.org/colomoto/pymaboss)
![build](https://github.com/colomoto/pyMaBoSS/workflows/build/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/colomoto/pyMaBoSS/badge.svg?branch=master)](https://coveralls.io/github/colomoto/pyMaBoSS?branch=master)
[![Documentation Status](https://readthedocs.org/projects/pymaboss/badge/?version=latest)](http://pymaboss.readthedocs.io/en/latest/?badge=latest)

Python interface for the MaBoSS software (https://maboss.curie.fr)

## Installation

### With conda

```
conda install -c colomoto pymaboss
```

### With pip

This is not the recommended option as it cannot yet package the MaBoSS binaries, but if you already have then install you can just install pyMaBoSS using
```
   pip install maboss
```

To download the MaBoSS binaries, if you have conda and if you are using linux or macosx, you can run : 
```
   python -m maboss_setup
```
  
If you are using Windows, or if the command above did not work, you can try to run : 
```
   python -m maboss_setup_experimental
```

Otherwise, you can download them using the following links, for [Linux](https://github.com/sysbio-curie/MaBoSS-env-2.0/releases/latest/download/MaBoSS-linux64.zip), [MacOSX arm64](https://github.com/sysbio-curie/MaBoSS-env-2.0/releases/latest/download/MaBoSS-osx-arm64.zip), [MacOSX X86_64](https://github.com/sysbio-curie/MaBoSS-env-2.0/releases/latest/download/MaBoSS-osx64.zip) or [Windows](https://github.com/sysbio-curie/MaBoSS-env-2.0/releases/latest/download/MaBoSS-win64.zip). Once downloaded, you need to extract them and make them accessible by putting them in a folder configured in your PATH. 


