# SGClima APIs
This repository holds the code that allows you to interact with the public APIs of SGClima. As of now it offers
support for the:
* Data API
* Models API (outdated as it has been some time since it has been updated)

## Installing this library

This library is available on the public repository of [PyPi](https://pypi.org/project/sgclimaapiclient/) as it has no
critical code.

If using `pip` simply run:

```shell
pip install sgclimaapiclient
```

If using `poetry` simply run:

```shell
poetry add sgclimaapiclient
```

## Creating a new version of the library

When you have made changes to the library and wish to make it available through you package manager you need to:

1. Increase the version number in the `sgclimaapiclient/version.py` file.

2. Push the changes to the main branch and wait for the pipeline to finish.