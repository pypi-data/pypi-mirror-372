# Picture blurring

Picture blurring can be enabled using the `API_BLUR_URL` environment variable, which should point to an API offering blurring services. The following services are compatible with Panoramax:

- [Panoramax blurring API](https://gitlab.com/panoramax/server/blurring)
- [SGBlur](https://github.com/cquest/sgblur)

Panoramax API stores directly blurred pictures, and if blurring is enabled, doesn't keep original unblurred pictures. This ensures a good level of privacy as required by European legislation.

You can change blur API URL at anytime if you want to use another service. Pictures already blurred are not blurred again when changing provider.

## Blur API specifications

If you want to plug another blur API than the ones listed above, you have to make sure that:

- It offers a `POST /blur/` route
  - That accepts `multipart/form-data`
  - Containing a JPEG picture file under `picture` parameter
  - And returns with a `200` code the same picture, blurred, in JPEG, with all original EXIF metadata
  - Optionally, the route can have a `keep=1` URL query parameter to keep unblurred parts

The blur API can also optionally return a `multipart/form-data` response (if the client asks for it through the `Accept` header), with the following parts:

- `image`: the blurred picture
- `metadata`: the blurring metadata, as a JSON object

The metadata object should contain the following fields:

- `blurring_id`: the blurring id, as a string. Used to unblur the picture later if the service supports it.
- `service_name`: the name of the service, as a string. This part needs to be stable since it will be used to cleanup the old semantics tags if a picture is blurred multiple times.
- `annotations`: a list of Panoramax annotations with semantic tags. This makes it possible to automatically add semantic tags on detected features (and not blurred) by the blur API. The annotations should be in the same format as the annotations returned by the `/annotations` routes. For the moment only `annotations` (semantics on part of the picture) are handled, not semantic tags on the whole picture.

Ths blurring API may also support an optional `keep=1` URL query parameter to keep unblurred parts. If it supports this, the kept blurring parts should not have any other metadata than the `blurring_id` and the part of the picture that was blurred, so that those parts could not be used without the blurring id. The service should also not keep those parts for too long.

