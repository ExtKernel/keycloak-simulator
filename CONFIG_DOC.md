# Configuration

Config should be a .cfg extension file:

```
[AUTH]
REALM=ISS
# Keycloak master(default) realm
# Sometimes they change it
MASTER_REALM=master
# OAuth2 endpoints
TOKEN_ENDPOINT=/realms/<realm>/protocol/openid-connect/token
INTROSPECT_ENDPOINT=/realms/<realm>/protocol/openid-connect/token/introspect
# Templates
TOKEN_RESPONSE_TEMPLATE=/path/to/token_response_template.json
INTROSPECT_RESPONSE_TEMPLATE=/path/to/introspect_response_template.json
REALM_ROLES_TEMPLATE=/path/to/realm_roles.json

[USER]
REALM=ISS
# Admin API endpoints
CREATE_USER_ENDPOINT=/admin/realms/<realm>/users
GET_USER_ENDPOINT=/admin/realms/<realm>/users/<user_id>
GET_USERS_ENDPOINT=/admin/realms/<realm>/users
RESET_USER_PASSWORD_ENDPOINT=/admin/realms/<realm>/users/<user_id>/reset-password
DELETE_USER_ENDPOINT=/admin/realms/<realm>/users/<user_id>
# Templates
ADMIN_USER_TEMPLATE=/path/to/admin.json
GET_USER_RESPONSE_TEMPLATE=/path/to/get_user_response_template.json
GET_USERS_RESPONSE_TEMPLATE=/path/to/get_users_response_template.json
```
`[AUTH]` and `[USERS]` - are mandatory names of the sections. In order to use different names,
a change in [app.py](app.py) will be needed at the following lines: 
- `config_handler.get_config('USER', config)`
- `config_handler.get_config('AUTH', config)`

`REALM` - Should be specified for both sections and meant to be identical for both. But can be different, if your use-case requires such configuration.
All the Admin REST API requests will be checked against value of this variable.

---
### Templates
Templates are supposed to reflect the actual Keycloak responses in case of successful request.
All the templates are present and preconfigured in this repository. **But not specified correctly in the example config above**.
Please replace "/path/to" with actual paths to the templates.

Empty strings or 0 integer values in the templates are meant to be filled during processing in the code or ignored.
#### User templates
- [ADMIN_USER_TEMPLATE](templates/user/admin.json) - An admin user will be created at the start of the simulator based on this template.
Responses of requests on the corresponding endpoints will be defined based on the following templates:
- [GET_USER_RESPONSE_TEMPLATE](templates/user/get_user_response_template.json)
- [GET_USERS_ENDPOINT](templates/user/get_users_response_template.json)
#### Auth templates
Responses of requests on the corresponding endpoints will be defined based on the following templates:
- [TOKEN_RESPONSE_TEMPLATE](templates/token/token_response_template.json)
- [INTROSPECT_RESPONSE_TEMPLATE](templates/token/introspect_response_template.json)
- [REALM_ROLES_TEMPLATE](templates/token/realm_roles.json) - Will be included in [INTROSPECT_RESPONSE_TEMPLATE](templates/token/introspect_response_template.json)
during processing in the code.
---
### Endpoint configuration
The endpoint configuration exists to avoid hardcoded endpoints. 
It should always reflect actual endpoints of Keycloak Admin REST API and OAuth2.
**with variables**. Variables (\<realm\>, \<user_id\>), in case of changing or adding new ones,
should be reflected in Flask endpoint functions(their arguments) and stay withing `<variable_name>` format.

**Note that** the config example above contains up-to-date endpoints according to the latest Keycloak documentation
at the moment of writing this.