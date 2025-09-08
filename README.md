# Keycloak simulator
A Keycloak Admin API simulator. Most suitable for simulating its behavior during integration testing.

Mainly created for testing [Identity Provider Synchronization Service](https://github.com/ExtKernel/idp-sync-service)

---
### Features

Auth-related requests:
- Get token
- Token introspection

User-related Admin API requests:
- Create user
- Get user by ID
- Get all users
- Reset user password
- Delete user by ID

User group-related Admin API requests:
- Create user group
- Get user group by id
- Get all user groups
- Delete user group by id

---
### Configuration
Creating a config is mandatory.
For configuration hints please see [config doc](CONFIG_DOC.md)
---
### Running
1) Clone this repository and navigate to the cloned directory 
```shell
git clone https://github.com/ExtKernel/keycloak-simulator.git; \
cd keycloak-simulator
```
2) Create an env and source it
```shell
python3 -m venv .venv; \
source .venv/bin/activate
```
3) Install packages
```shell
pip install -r requirements.txt
```
4) Specify a config and run
```shell
python3 app.py /path/to/your/config.cfg
```