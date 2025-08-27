# coding=utf-8

import re

TyBool = bool
TyStr = str


class Uri:

    @staticmethod
    def verify(uri: TyStr) -> TyBool:
        uri_regex = re.compile(
          r'^(?:http|ftp)s?://'  # http:// or https://
          r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
          r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
          r'localhost|'  # localhost...
          r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
          r'(?::\d+)?'  # optional port
          r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(uri_regex, uri) is not None
