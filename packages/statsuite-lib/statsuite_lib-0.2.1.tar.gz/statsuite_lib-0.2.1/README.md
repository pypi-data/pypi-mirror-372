# StatSuite-lib

StatSuite-lib is an opinionated library to interact with dotStatSuite components.
There is no full coverage of the APIs, it will be completed as needed.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install statsuite-lib.

```bash
pip install statsuite-lib
```

## Usage

Check the documentation, mainly the statsuite-cli repo can serve as example on how to use this library
Keycloak client must be initialized and pass to any other client requiring authentication to manage the token creation and renewal

```python
from statsuite_lib import SFSClient, KeycloakClient


OPENID_URL = "http://localhost:8080/auth/realms/demo/.well-known/openid-configuration"
KEYCLOAK_USER = 'test-admin'
KEYCLOAK_PASSWORD = 'admin'
SFS_API_KEY = 'secret'
SFS_URL = 'http://localhost:3004'

keycloak = KeycloakClient(openid_url=OPENID_URL,
                          username=KEYCLOAK_USER,
                          password=KEYCLOAK_PASSWORD)


sfs = SFSClient(sfs_url=SFS_URL, sfs_api_key=SFS_API_KEY)

id = sfs.index()

print(f"Index started with id {id}")
sfs.wait_for_reindex_to_finish(loading_id=id, tenant='default')
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)