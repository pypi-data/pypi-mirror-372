# Using the HTTP API

By default, your Panoramax HTTP API is available on [localhost:5000](http://localhost:5000/).

The HTTP API allows you to access to collections (sequences), items (pictures) and their metadata. Panoramax API is following the [STAC API specification](https://github.com/radiantearth/stac-api-spec/blob/main/overview.md), which is based on OGC API and a widely-used standard for geospatial imagery. More info about STAC [is available online](https://stacspec.org/en).

!!! tip "OpenAPI :simple-openapiinitiative:"

    API routes are documented is the [OpenAPI section](./openapi.md), and you can check your instance :simple-swagger: Swagger documentation in the route `/api/docs/swagger` ([like this for the IGN instance](https://panoramax.ign.fr/api/docs/swagger)). 

## 🔐 Authentication

If activated at the Panoramax's instance level, some routes might need authentication.

### OAuth flow

The main way to authenticate on the API is based on [OAuth 2.0](https://wikipedia.org/wiki/OAuth).

The authentication is asked to the configured instance's OAuth provider and stored in a session cookie.

The routes that need authentication should redirect to the `/api/auth/login` route if no session cookie is set.

A logout from the instance can be done via the `/api/auth/logout` route.

### :simple-jsonwebtokens: Bearer token

Protected routes can also be accessed with a [:simple-jsonwebtokens: JWT](https://wikipedia.org/wiki/JSON_Web_Token) [Bearer token](https://datatracker.ietf.org/doc/html/rfc6750).

Those tokens are needed when using the API without a browser, for example when doing regular [curl](https://curl.se/) calls or with our __[command-line client](https://gitlab.com/panoramax/clients/cli)__.

The JWT token should be given to the API via the `Authorization` header as a bearer token.

=== ":simple-curl: curl"

    Considering your Panoramax server is `https://my-panoramax.fr/`, you can do:

    ```bash
    curl https://my-panoramax.fr/api/users/me --header "Authorization: Bearer <A_JWT_TOKEN>"
    ```

=== ":simple-httpie: httpie"

    And with [httpie](https://httpie.io) (at least httpie 3.0.0 is needed):

    ```bash
    http -A bearer -a <A_JWT_TOKEN> https://my-panoramax.fr/api/users/me
    ```

#### How to get a token

##### Via an OAuth logged call

To get a JWT token, a regular user need to use a browser and call `/api/users/me/tokens`.

This will trigger an OAuth dance, and if the OAuth provider validates the user's credentials, this will return a list of Panoramax tokens like:

```json
[
  {
    "description": "default token",
    "generated_at": "2023-05-11T15:56:59.410095+00:00",
    "id": "e11c255c-6023-4eee-bb47-31566f4ce65f",
    "links": [
      {
        "href": "https://my-panoramax.fr/api/users/me/tokens/e11c255c-6023-4eee-bb47-31566f4ce65f",
        "rel": "self",
        "type": "application/json"
      }
    ]
  }
]
```

A Panoramax token can be converted to a JWT token by calling (also in a browser, since an authenticated session cookie is needed):

`api/users/me/tokens/:id` with the ID of a token.

This will return a json with a `jwt_token` field which is the token needed as Bearer token.

An example result would be:
```json
{
  "description": "default token",
  "generated_at": "2023-05-11T15:56:59.410095+00:00",
  "id": "e11c255c-6023-4eee-bb47-31566f4ce65f",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnZW92aXNpbyIsInN1YiI6ImUxMWMyNTVjLTYwMjMtNGVlZS1iYjQ3LTMxNTY2ZjRjZTY1ZiJ9.vGJz-AgFgP4T5pZqGVK49-HcZXvOeFZm3EEIYrAJ44M"
}
```

With this example, accessing a protected route with this jwt token could be done with:

=== ":simple-curl: curl"

    Considering your Panoramax server is `https://my-panoramax.fr/`, you can do:

    ```bash
    curl https://my-panoramax.fr/api/users/me --header "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnZW92aXNpbyIsInN1YiI6ImUxMWMyNTVjLTYwMjMtNGVlZS1iYjQ3LTMxNTY2ZjRjZTY1ZiJ9.vGJz-AgFgP4T5pZqGVK49-HcZXvOeFZm3EEIYrAJ44M"
    ```

=== ":simple-httpie: httpie"

    And with [httpie](https://httpie.io) (at least httpie 3.0.0 is needed):

    ```bash
    http -A bearer -a eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnZW92aXNpbyIsInN1YiI6ImUxMWMyNTVjLTYwMjMtNGVlZS1iYjQ3LTMxNTY2ZjRjZTY1ZiJ9.vGJz-AgFgP4T5pZqGVK49-HcZXvOeFZm3EEIYrAJ44M https://my-panoramax.fr/api/users/me
    ```

##### Via pregenerated token

Tokens can be fearsome, but Panoramax support a nicer way to generate them.

A token not associated to any account can be generated with a POST on `/api/auth/tokens/generate`:

=== ":simple-curl: curl"

    Considering your Panoramax server is `https://my-panoramax.fr/`, you can do:

    ```bash
    curl -X POST https://my-panoramax.fr/api/auth/tokens/generate
    ```

=== ":simple-httpie: httpie"

    And with [httpie](https://httpie.io) (at least httpie 3.0.0 is needed):

    ```bash
    http POST https://my-panoramax.fr/api/auth/tokens/generate
    ```

This will return a new token, with its JWT counterpart like:

```json
{
  "description": "",
  "generated_at": "2023-05-23T15:58:26.645393+00:00",
  "id": "ee649235-bf10-4b04-a09a-64b1663af6f8",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnZW92aXNpbyIsInN1YiI6ImVlNjQ5MjM1LWJmMTAtNGIwNC1hMDlhLTY0YjE2NjNhZjZmOCJ9.MoZYN9gsqiCQL3GrN2k6fZ21msrxFFtAZSEA3ClkKc0",
  "links": [
    {
      "href": "https://my-panoramax.fr/api/auth/tokens/ee649235-bf10-4b04-a09a-64b1663af6f8/claim",
      "rel": "claim",
      "type": "application/json"
    }
  ]
}
```

This JWT token can be saved somewhere, but will not be usable until an account is associated with it.

An account can be associated with it by opening in a browser the `claim` url in the `links` section. (the url `https://my-panoramax.fr/api/auth/tokens/ee649235-bf10-4b04-a09a-64b1663af6f8/claim` in the example below).

Opening the URL will trigger an OAuth dance in the browser, and if the user is successfully logged in, the token will be associated to its account.

[Panoramax CLI](https://gitlab.com/panoramax/clients/cli) uses this mechanism to hide token complexity to the users.

##### JWT token for the instance administrator

An instance administrator can get the JWT token of the default instance's account with the flask command `default-account-tokens get`, see the [administrating section](../install/cli.md#jwt-token-for-the-instance-administrator) for more details.

!!! warning

    Be sure not to share this token!

#### Revoking a token

A token can be revoked (definitely deleted) by calling a `DELETE` on `/api/users/me/tokens/<uuid:token_id>`

This calls needs to be logged, another token (or even the same one) can be used.

=== ":simple-curl: curl"

    ```bash
    curl -XDELETE https://my-panoramax.fr/api/users/me/tokens/ee649235-bf10-4b04-a09a-64b1663af6f8 --header "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnZW92aXNpbyIsInN1YiI6ImVlNjQ5MjM1LWJmMTAtNGIwNC1hMDlhLTY0YjE2NjNhZjZmOCJ9.MoZYN9gsqiCQL3GrN2k6fZ21msrxFFtAZSEA3ClkKc0"
    ```

=== ":simple-httpie: httpie"

    ```bash
    http  -A bearer -a eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnZW92aXNpbyIsInN1YiI6ImVlNjQ5MjM1LWJmMTAtNGIwNC1hMDlhLTY0YjE2NjN DELETE https://my-panoramax.fr/api/users/me/tokens/ee649235-bf10-4b04-a09a-64b1663af6f8
    ```


## :octicons-upload-16: Upload

Panoramax also offers API routes to upload pictures. Many ways are available to work with upload API, like using the __[command-line client](https://docs.panoramax.fr/cli/)__ or through any [instance website](https://docs.panoramax.fr/how-to-contribute/#choose-where-to-share-them).

You can also use a third-party tool to work directly with HTTP requests. Upload should go through different steps.

You can go through these steps with the following _cURL_ bash commands (considering your Panoramax server is `https://my-panoramax.fr/`):

!!! Note

    Most instances require an authentication for uploading pictures, check the [🔐 Authentication](#authentication) section to know how to pass an authentication token

### 1. 📁 Upload set creation

Create an 📁 _upload set_ (a batch of uploaded pictures) with `POST /api/upload_sets`. It will give you back an upload set ID that you will need for next steps.
If possible, set the number of files that will be sent on this upload set.


=== ":simple-curl: curl"

    ```bash
    curl -X POST https://my-panoramax.fr/api/upload_sets -d '{"title": "some title", "estimated_nb_files": 2}' --header "Content-Type: application/json"
    ```

=== ":simple-httpie: httpie"

    ```bash
    http https://my-panoramax.fr/api/upload_sets title="some title" estimated_nb_files=2
    ```


!!! Note

    Check the [API documentation](openapi.md) to discover all the parameters that can be given to the upload set creation. 
    
    They might be used to control the dispatch into collections, the pictures deduplication and sorting, ...

You will have in both Location HTTP response header and in JSON response body the upload set ID.
We consider below upload set ID :identification_card: is `60d94628-8098-42cc-b684-ffb9aa9d35a7`

### 2. :material-upload: Upload pictures

Upload as many pictures as wanted with `POST /api/upload_sets/<UPLOAD_SET ID>/items`. A JPEG image file is needed.

=== ":simple-curl: curl"

    ```bash
    curl -X POST https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7/files -F file=@my_picture_001.jpg
    ```

=== ":simple-httpie: httpie"

    ```bash
    http https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7/files --form file@my_picture_001.jpg
    ```

Send as many pictures as specified in the provided `estimated_nb_files`.

!!! Note
    
    Invalid pictures with for example bad metadata will be rejected but still counted as a received file, so the whole process will still be completed, even if some pictures were rejected.

If the number of files cannot be known in advance or if something came up and all the files cannot be sent, the upload set needs to be `completed` in order for the pictures to be publicly available.

=== ":simple-curl: curl"

    ```bash
    curl -X POST https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7/complete
    ```

=== ":simple-httpie: httpie"

    ```bash
    http POST https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7/complete
    ```

!!! Note

    The names of the files should be unique in the upload, so a client can send a picture again after changing its metadata.

### 3. ⏲️ Wait while checking for processing status

The pictures need to be prepared (blurred and derivates needs to be generated) and when everything has been received the pictures are dispatched to one or more collections and useless pictures like when stopped at a traffic light are detected and deleted.

This is done asynchronously, so the waiting time can depend on the server load.

You can check status using `GET /api/upload_sets/<UPLOAD_SET ID>` to see the progress made on process.

=== ":simple-curl: curl"

    ```bash
    curl https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7
    ```

=== ":simple-httpie: httpie"

    ```bash
    http https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7
    ```

The field `items_status` will tell you the status of each item in the upload set and its associated collections.

The field `ready` is an easy way to check if all the collections have been created and all the pictures are ready to be served.

!!! Info

    The _dispatch_ step done on API consist in creating as many collections as needed based on your upload set. A collection is a continuous sequence of pictures, within a certain time and distance range. So if two pictures are too distant or taken after too much time, a new collection is created.

#### :material-file-image: Status of each received files

You can check the status of each received files.

=== ":simple-curl: curl"

    ```bash
    curl https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7/files
    ```

=== ":simple-httpie: httpie"

    ```bash
    http https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7/files
    ```

This is especially useful if you want to check if a picture was rejected, or if it has been detected as a capture duplicate (like for example if several pictures were taken when stopping at a traffic light). In those cases, the file will have a `rejected` field with the reason.

This call can also help if a client needs to know if it has sent everything it meant to.

### 4. 📸 Enjoy you pictures

Enjoy your brand-new uploaded pictures by browsing the map or querying the associated collections with  `GET /api/upload_sets/<UPLOAD_SET ID>` !

=== ":simple-curl: curl"

    ```bash
    curl https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7
    ```

=== ":simple-httpie: httpie"

    ```bash
    http https://my-panoramax.fr/api/upload_sets/60d94628-8098-42cc-b684-ffb9aa9d35a7
    ```