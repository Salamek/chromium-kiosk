from __future__ import annotations

import shutil
import urllib.parse


def inject_parameters_to_url(url: str, parameters: dict) -> str:

    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(parameters)

    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


def find_binary(names: list[str]) -> str | None:
    """
    Find binary
    :return:
    """
    for name in names:
        found = shutil.which(name)
        if found:
            return found

    return None

