[![](https://img.shields.io/badge/Version-1.0.1-_)](https://pypi.org/project/sprite.server/)
[![](https://img.shields.io/badge/Platform-windows%20|%20linux%20|%20osx-_)](https://pypi.org/project/sprite.server/)

# Sprite Server

Sprite Server is a simple static server. A simple command can start the service. Files can be uploaded and downloaded without configuration. It can be used for development, testing and learning.

<font color="#dd0000">Note: Do not use in production environments.</font>

## Features

* Download files from the server.

* Select the files and upload them to the server directory.

* Upload files to the server directory by dragging and dropping.


## Installation

### Install via pip:

```shell
pip install sprite.server
```

## Usage

### Start server

```shell
# The default port number is 6060
python -m sprite.server [port number]
```

### Access server

Visit: [http://localhost:6060](http://localhost:6060)

## Options

| Option | Description | Defaults |
|  ----  | ----  | ---- |
| &lt;port&gt; | Port to use. | 6060 |
| -v, --version | Show version number. |
| -h, --help | Print this list. |

**Enjoy!**






