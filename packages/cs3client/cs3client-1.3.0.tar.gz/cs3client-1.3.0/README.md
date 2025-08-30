# CS3Client

`CS3Client` is a Python client for interacting with the CS3 (Cloud Sync&Share Storage) [APIs](https://github.com/cs3org/cs3apis). It allows users to seamlessly communicate with cloud storage services that support CS3 protocols, enabling file management, data transfer, and other cloud-based operations.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Documentation](#documentation)
- [License](#license)


## Features

- Simple and easy-to-use API client for CS3 services.
- Support for common file operations (read, write, delete, rename, ...).
- Support for common lock operations (set lock, get lock, unlock, ...).
- Support for common share operations (create share, update share, delete share, ...).
- Support for common user operations (get user, find users, get user groups, ...).
- Support for restoring files through checkpoints (restore file version, list checkpoints).
- Support for applications (open in app, list app providers).
- Authentication and authorization handling.
- Cross-platform compatibility.
- Detailed error handling and logging.

## Installation

To install `cs3client`, you need to have Python 3.7+ installed. You can install the package via `pip`:

```bash
pip install cs3client
```
Alternatively, you can clone this repository and install manually:
```bash
git clone git@github.com:cs3org/cs3-python-client.git
cd cs3-python-client
pip install . 
```


## Configuration

`CS3Client` can be configured by passing specific parameters when initializing the client through a ConfigParser instance.

### Parameters:

#### Required
- `host`

#### Optional (parameter - default)
- `chunk_size` - 4194384
- `grpc_timeout` - 10
- `http_timeout` - 10
- `tus_enabled` - False
- `ssl_enabled` - False
- `ssl_client_cert` - None
- `ssl_client_key` - None
- `ssl_ca_cert` - None
- `auth_client_id` - None
- `auth_login_type` - "basic"
- `lock_by_setting_attr` - False
- `lock_not_impl` - False
- `lock_expiration` - 1800

#### Example configuration
```yaml
[cs3client]

# Required
host = localhost:19000
# Optional, defaults to 4194304
chunk_size = 4194304
# Optional, defaults to 10
grpc_timeout = 10
# Optional, defaults to 10
http_timeout = 10

# Optional, defaults to True
tus_enabled = False

# Optional, defaults to True
ssl_enabled = False
# Optional, defaults to True
ssl_verify = False
# Optional, defaults to an empty string
ssl_client_cert = test_client_cert
# Optional, defaults to an empty string
ssl_client_key = test_client_key
# Optional, defaults to an empty string
ssl_ca_cert = test_ca_cert

# Optinal, defaults to an empty string
auth_client_id = einstein
# Optional (can also be set when instansiating the class)
auth_client_secret = relativity
# Optional, defaults to basic
auth_login_type = basic

# Optional, defaults to False
lock_by_setting_attr = False
# Optional, defaults to False
lock_not_impl = False
# Optional, defaults to 1800
lock_expiration = 1800


```

## Usage

To use `cs3client`, you first need to import and configure it. Here's a simple example of how to set up and start using the client. For configuration see [Configuration](#configuration). For more in depth examples see `cs3-python-client/examples/`. 

### Initilization and Authentication
```python
import logging
import configparser
from cs3client.cs3client import CS3Client
from cs3client.auth import Auth

config = configparser.ConfigParser()
with open("default.conf") as fdef:
    config.read_file(fdef)
log = logging.getLogger(__name__)

client = CS3Client(config, "cs3client", log)
auth = Auth(client)
# Set the client id (can also be set in the config)
auth.set_client_id("<your_client_id_here>")
# Set client secret (can also be set in config)
auth.set_client_secret("<your_client_secret_here>")
# Checks if token is expired if not return ('x-access-token', <token>)
# if expired, request a new token from reva
auth_token = auth.get_token()

# OR if you already have a reva token
# Checks if token is expired if not return (x-access-token', <token>)
# if expired, throws an AuthenticationException (so you can refresh your reva token)
token = "<your_reva_token>"
auth_token = Auth.check_token(token)

```

### File Example
```python
# mkdir
directory_resource = Resource(abs_path=f"/eos/user/r/rwelande/test_directory")
res = client.file.make_dir(auth.get_token(), directory_resource)

# touchfile
touch_resource = Resource(abs_path="/eos/user/r/rwelande/touch_file.txt")
res = client.file.touch_file(auth.get_token(), touch_resource)

# setxattr
resource = Resource(abs_path="/eos/user/r/rwelande/text_file.txt")
res = client.file.set_xattr(auth.get_token(), resource, "iop.wopi.lastwritetime", str(1720696124))

# rmxattr
res = client.file.remove_xattr(auth.get_token(), resource, "iop.wopi.lastwritetime")

# stat
res = client.file.stat(auth.get_token(), resource)

# removefile
res = client.file.remove_file(auth.get_token(), touch_resource)

# rename
rename_resource = Resource(abs_path="/eos/user/r/rwelande/rename_file.txt")
res = client.file.rename_file(auth.get_token(), resource, rename_resource)

# writefile
content = b"Hello World"
size = len(content)
res = client.file.write_file(auth.get_token(), rename_resource, content, size)

# listdir
list_directory_resource = Resource(abs_path="/eos/user/r/rwelande")
res = client.file.list_dir(auth.get_token(), list_directory_resource)


# readfile
file_res = client.file.read_file(auth.get_token(), rename_resource)
```
### Lock Example
```python

WEBDAV_LOCK_PREFIX = 'opaquelocktoken:797356a8-0500-4ceb-a8a0-c94c8cde7eba'


def encode_lock(lock):
    '''Generates the lock payload for the storage given the raw metadata'''
    if lock:
        return WEBDAV_LOCK_PREFIX + ' ' + b64encode(lock.encode()).decode()
    return None

resource = Resource(abs_path="/eos/user/r/rwelande/lock_test.txt")

# Set lock
client.file.set_lock(auth_token, resource, app_name="a", lock_id=encode_lock("some_lock"))

# Get lock
res = client.file.get_lock(auth_token, resource)
if res is not None:
    lock_id = res["lock_id"]
    print(res)

# Unlock
res = client.file.unlock(auth_token, resource, app_name="a", lock_id=lock_id)

# Refresh lock
client.file.set_lock(auth_token, resource, app_name="a", lock_id=encode_lock("some_lock"))
res = client.file.refresh_lock(
    auth_token, resource, app_name="a", lock_id=encode_lock("new_lock"), existing_lock_id=lock_id
)

if res is not None:
    print(res)

res = client.file.get_lock(auth_token, resource)
if res is not None:
    print(res)

```

### Share Example
```python
# Create share #
resource = Resource(abs_path="/eos/user/r/<some_username>/text.txt")
resource_info = client.file.stat(auth.get_token(), resource)
user = client.user.get_user_by_claim("username", "<some_username>")
res = client.share.create_share(auth.get_token(), resource_info, user.id.opaque_id, user.id.idp, "EDITOR", "USER")

# List existing shares #
filter_list = []
filter = client.share.create_share_filter(resource_id=resource_info.id, filter_type="TYPE_RESOURCE_ID")
filter_list.append(filter)
filter = client.share.create_share_filter(share_state="SHARE_STATE_PENDING", filter_type="TYPE_STATE")
filter_list.append(filter)
res, _ = client.share.list_existing_shares(auth.get_token(), )

# Get share #
share_id = "58"
res = client.share.get_share(auth.get_token(), opaque_id=share_id)

# update share #
res = client.share.update_share(auth.get_token(), opaque_id=share_id, role="VIEWER")

# remove share #
res = client.share.remove_share(auth.get_token(), opaque_id=share_id)

# List existing received shares #
filter_list = []
filter = client.share.create_share_filter(share_state="SHARE_STATE_ACCEPTED", filter_type="TYPE_STATE")
filter_list.append(filter)
res, _ = client.share.list_received_existing_shares(auth.get_token())

# get received share #
received_share = client.share.get_received_share(auth.get_token(), opaque_id=share_id)

# update recieved share #
res = client.share.update_received_share(auth.get_token(), received_share=received_share, state="SHARE_STATE_ACCEPTED")

# create public share #
res = client.share.create_public_share(auth.get_token(), resource_info, role="VIEWER")

# list existing public shares #
filter_list = []
filter = client.share.create_public_share_filter(resource_id=resource_info.id, filter_type="TYPE_RESOURCE_ID")
filter_list.append(filter)
res, _ = client.share.list_existing_public_shares(filter_list=filter_list)

res = client.share.get_public_share(auth.get_token(), opaque_id=share_id, sign=True)
# OR token = "<token>"
# res = client.share.get_public_share(token=token, sign=True)

# update public share #
res = client.share.update_public_share(auth.get_token(), type="TYPE_PASSWORD", token=token, role="VIEWER", password="hello")

# remove public share #
res = client.share.remove_public_share(auth.get_token(), token=token)

```

### User Example
```python
# find_user
res = client.user.find_users(auth.get_token(), "rwel")

# get_user
res = client.user.get_user("https://auth.cern.ch/auth/realms/cern", "asdoiqwe")

# get_user_groups
res = client.user.get_user_groups("https://auth.cern.ch/auth/realms/cern", "rwelande")

# get_user_by_claim (mail)
res = client.user.get_user_by_claim("mail", "rasmus.oscar.welander@cern.ch")

# get_user_by_claim (username)
res = client.user.get_user_by_claim("username", "rwelande")

```

### App Example
```python
# list_app_providers
res = client.app.list_app_providers(auth.get_token())

# open_in_app
resource = Resource(abs_path="/eos/user/r/rwelande/collabora.odt")
res = client.app.open_in_app(auth.get_token(), resource)
```

### Checkpoint Example
```python
# list file versions
resource = Resource(abs_path="/eos/user/r/rwelande/test.md")
res = client.checkpoint.list_file_versions(auth.get_token(), resource)

# restore file version
res = client.checkpoint.restore_file_version(auth.get_token(), resource, "1722936250.0569fa2f")
```

## Documentation
The documentation can be generated using sphinx

```bash
pip install sphinx
cd docs
make html
```

## Unit tests

```bash
pytest --cov-report term --cov=serc tests/
```

## License

This project is licensed under the Apache 2.0 License. See the LICENSE file for more details.
