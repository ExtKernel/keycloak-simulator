### OAuth2.0
Keycloak OAuth2.0 functionality simulation.

| Feature                                          | Approximate completeness | Required?    | Note                                                                                                                                                                           |
|--------------------------------------------------|--------------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Basic endpoint simulation                        | 60%                      | Yes          |                                                                                                                                                                                |
| Request validation                               | ---                      | Yes          | Realm validation broken                                                                                                                                                        |
| Dynamic configurable Access Token representation | 0%                       | Good to have |                                                                                                                                                                                |
| Dynamic configuration error handling             | 0%                       | Good to have |                                                                                                                                                                                |
| Endpoint dynamic configuration                   | 80%                      | Yes          | Hardcoded OpenID Connect Well-Known and Certs endpoint paths                                                                                                                   |
| Responses based on dynamic templates             | 50%                      | Yes          | OpenID Connect Well-Known and Certs endpoint response templates are being used as-is with hardcoded values.<br/>Introspect endpoint response template building needs revision. |

### User
Keycloak Realm User-related functionality simulation.

| Feature                                  | Approximate completeness | Required?    | Note                                                        |
|------------------------------------------|--------------------------|--------------|-------------------------------------------------------------|
| Basic endpoint simulation                | 100%                     | Yes          |                                                             |
| Request validation                       | 10%                      | Yes          | Only Realm validation done                                  |
| Dynamic configurable User representation | 80%                      | Good to have |                                                             |
| Dynamic configuration error handling     | 25%                      | Good to have | Will build even with any arguments if required are presents |
| Admin CLI user initialization by default | 100%                     | Yes          |                                                             |
| Responses based on dynamic templates     | 100%                     | Yes          |                                                             |

### User group
Keycloak Realm User group-related functionality simulation.

| Feature                                        | Approximate completeness | Required?    | Note                                                        |
|------------------------------------------------|--------------------------|--------------|-------------------------------------------------------------|
| Basic endpoint simulation                      | 100%                     | Yes          |                                                             |
| Request validation                             | 10%                      | Yes          | Only Realm validation done                                  |
| Dynamic configurable User group representation | 80%                      | Good to have |                                                             |
| Dynamic configuration error handling           | 15%                      | Good to have | Will build even with any arguments if required are presents |
| Responses based on dynamic templates           | 95%                      | Yes          |                                                             |

### Client
Keycloak Realm Client-related functionality simulation.

| Feature                                    | Approximate completeness | Required?         | Note                                      |
|--------------------------------------------|--------------------------|-------------------|-------------------------------------------|
| Basic endpoint simulation                  | 20%                      | Yes               | Only Client creation endpoint present     |
| Request validation                         | 10%                      | Yes               | Only Realm validation done                |
| Dynamic configurable Client representation | 70%                      | Good to have      | Still a lot of hardcode                   |
| Responses based on dynamic templates       | 0%                       | Not at this point | Not required for Client creation endpoint |