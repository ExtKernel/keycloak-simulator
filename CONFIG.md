Config should be a .cfg extension file. The following example can be copy-pasted into your config file,
besides `REALM` which should be changed according to your Keycloak setup.
```
[Keycloak]
REALM=ISS
TOKEN_ENDPOINT=/realms/<realm>/protocol/openid-connect/token
INTROSPECT_ENDPOINT=/realms/<realm>/protocol/openid-connect/token/introspect
# Admin API endpoints
# User
CREATE_USER_ENDPOINT=/admin/realms/<realm>/users
GET_USER_ENDPOINT=/admin/realms/<realm>/users/<user_id>
GET_USERS_ENDPOINT=/admin/realms/<realm>/users
RESET_USER_PASSWORD_ENDPOINT=/admin/realms/<realm>/users/<user_id>/reset-password
DELETE_USER_ENDPOINT=/admin/realms/<realm>/users/<user_id>
```
[Keycloak] - is a mandatory header. In order to work with a different name of the header,
you should change its name on `return dict(config.items('Keycloak'))` line in [utils.py](utils.py) file.
- `REALM` - expected Keycloak Realm for the request. 
The one given in the url of an incoming request will be compared to a value of this field.
---
The following configuration exists to avoid hardcoded endpoints. 
It should always reflect endpoints of Keycloak Admin REST API and OAuth2
**with variables**. Variables (\<realm\>, \<user_id\>), in case of changing or adding new ones,
should be reflected in Flask endpoint functions(their arguments) and stay withing `<variable_name>` format.
- `TOKEN_ENDPOINT` - Keycloak token endpoint
- `INTROSPECT_ENDPOINT` - Keycloak token introspect endpoint

Keycloak Admin REST API endpoints:
- `CREATE_USER_ENDPOINT` - Keycloak Admin REST API endpoint for creating a user
- `GET_USERS_ENDPOINT` - Get all users endpoint
- `RESET_USER_PASSWORD_ENDPOINT` - Reset user's password endpoint
- `DELETE_USER_ENDPOINT` - Delete a user endpoint
