from typing import Optional, Dict

from flask import url_for

from geovisio import web

WEBSITE_UNDER_SAME_HOST = "same-host"

TOKEN_ACCEPTED_PAGE = "token-accepted"
TOS_VALIDATION_PAGE = "tos-validation"


class Website:
    """Website associated to the API.
    This wrapper will define the routes we expect from the website.

    We should limit the interaction from the api to the website, but for some flow (especially auth flows), it's can be useful to redirect to website's page

    If the url is:
    * set to `false`, there is no associated website
    * set to `same-host`, the website is assumed to be on the same host as the API (and will respect the host of the current request)
    * else it should be a valid url
    """

    def __init__(self, website_url: str):
        if website_url == WEBSITE_UNDER_SAME_HOST:
            self.url = WEBSITE_UNDER_SAME_HOST
        elif website_url == "false":
            self.url = None
        elif website_url.startswith("http"):
            self.url = website_url
            if not self.url.endswith("/"):
                self.url += "/"
        else:
            raise Exception(
                "API_WEBSITE_URL should either be `same-host` (and the website will be assumed to be on the same host), set to `false` if there is no website, or a valid URL"
            )

    def _to_url(self, route: str, params: Optional[Dict[str, str]] = None):
        if not self.url:
            return None

        base_url = self.url if self.url != WEBSITE_UNDER_SAME_HOST else url_for("index", _external=True)

        from urllib.parse import urlencode

        return f"{base_url}{route}{f'?{urlencode(params)}' if params else ''}"

    def tos_validation_page(self, params: Optional[Dict[str, str]] = None):
        return self._to_url(TOS_VALIDATION_PAGE, params)

    def cli_token_accepted_page(self, params: Optional[Dict[str, str]] = None):
        return self._to_url(TOKEN_ACCEPTED_PAGE, params)
