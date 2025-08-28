# coding=utf-8
from typing import Any

import re

TyBool = bool
TyDic = dict[Any, Any]
TyStr = str
TyUri = str


class Uri:

    @staticmethod
    def verify(uri: TyUri) -> TyBool:
        uri_regex = re.compile(
          r'^(?:http|ftp)s?://'  # http:// or https://
          r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
          r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
          r'localhost|'  # localhost...
          r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
          r'(?::\d+)?'  # optional port
          r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(uri_regex, uri) is not None

    @staticmethod
    def add_params(uri: TyUri, params: TyDic) -> TyUri:
        from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

        # Parse the URL
        url_parts = list(urlparse(uri))

        # Update query parameters
        query = dict(parse_qs(url_parts[4]))
        query.update(params)

        # Rebuild the URL
        url_parts[4] = urlencode(query, doseq=True)
        new_url = urlunparse(url_parts)

        return new_url
