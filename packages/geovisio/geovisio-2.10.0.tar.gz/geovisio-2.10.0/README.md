# ![Panoramax](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Panoramax.svg/40px-Panoramax.svg.png) Panoramax

__Panoramax__ is a digital resource for sharing and using 📍📷 field photos. Anyone can take photographs of places visible from the public streets and contribute them to the Panoramax database. This data is then freely accessible and reusable by all. More information available at [gitlab.com/panoramax](https://gitlab.com/panoramax) and [panoramax.fr](https://panoramax.fr/).


# 🌐 Panoramax API

This repository only contains __the backend and web API__ of a Panoramax instance.

## Features

* A __web API__ to search and upload pictures collections
  * Search pictures by ID, date, location
  * Compatible with [SpatioTemporal Asset Catalog](https://stacspec.org/) and [OGC WFS 3](https://github.com/opengeospatial/WFS_FES) specifications
  * Upload your pictures and sequences
* An easy-to-use __backend__
  * Generates automatically thumbnail, small and tiled versions of your pictures
  * Compatible with various filesystems (classic, S3, FTP...)
  * Authentication and blurring API can be plugged-in for production-ready use


## Install & run

Our [documentation](https://gitlab.com/panoramax/server/api/-/tree/develop/docs) will help you install, configure and run a Panoramax instance.

If at some point you're lost or need help, you can contact us through [issues](https://gitlab.com/panoramax/server/api/-/issues) or by [email](mailto:panieravide@riseup.net).


## Contributing

Pull requests are welcome. For major changes, please open an [issue](https://gitlab.com/panoramax/server/api/-/issues) first to discuss what you would like to change.

More information about developing is available in [documentation](https://gitlab.com/panoramax/server/api/-/tree/develop/docs).


## ⚖️ License

Copyright (c) Panoramax team 2022-2024, [released under MIT license](https://gitlab.com/panoramax/server/api/-/blob/develop/LICENSE).
