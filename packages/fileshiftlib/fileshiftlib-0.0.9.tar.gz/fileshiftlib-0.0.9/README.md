# fileshiftlib

* [Description](#package-description)
* [Usage](#usage)
* [Installation](#installation)
* [License](#license)

## Package Description

SFTP client Python package that uses [paramiko](https://pypi.org/project/paramiko/) library.

## Usage

* [fileshiftlib](#fileshiftlib)

from a script:

```python
import fileshiftlib

host = "localhost"
username = "123..."
password = "xxxx"
port = 22

# Initialize SFTP client
sftp = fileshiftlib.SFTP(host=host,
                         username=username,
                         password=password,
                         port=port,
                         logger=None)
```

```python
content_list = sftp.list_dir()
print(content_list)
```

```python
sftp.change_dir(path=".")
```

```python
sftp.delete_file(filename=r"demo.txt")
```

```python
sftp.download_file(remote_path=r"/demo/demo.txt", local_path=r"c:\local\demo.txt")
```

```python
sftp.upload_file(local_path=r"c:\local\demo.txt", remote_path=r"/demo/demo.txt")
```

## Installation

* [fileshiftlib](#fileshiftlib)

Install python and pip if you have not already.

Then run:

```bash
pip install pip --upgrade
```

For production:

```bash
pip install fileshiftlib
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:

```bash
git clone https://github.com/aghuttun/fileshiftlib.git
cd fileshiftlib
pip install -e ".[dev]"
```

To test the development package: [Testing](#testing)

## License

* [fileshiftlib](#fileshiftlib)

BSD License (see license file)
