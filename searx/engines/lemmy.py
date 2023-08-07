# SPDX-License-Identifier: AGPL-3.0-or-later
# lint: pylint
"""This engine uses the Lemmy API (https://lemmy.ml/api/v3/search), which is
documented at `lemmy-js-client`_ / `Interface Search`_.  Since Lemmy is
federated, results are from many different, independent lemmy instances, and not
only the official one.

.. _lemmy-js-client: https://join-lemmy.org/api/modules.html
.. _Interface Search: https://join-lemmy.org/api/interfaces/Search.html

Configuration
=============

The engine has the following additional settings:

- :py:obj:`base_url`
- :py:obj:`lemmy_type`

This implementation is used by different lemmy engines in the :ref:`settings.yml
<settings engine>`:

.. code:: yaml

  - name: lemmy communities
    lemmy_type: Communities
    ...
  - name: lemmy users
    lemmy_type: Users
    ...
  - name: lemmy posts
    lemmy_type: Posts
    ...
  - name: lemmy comments
    lemmy_type: Comments
    ...

Implementations
===============

"""

from urllib.parse import urlencode
from markdown_it import MarkdownIt
from searx.utils import html_to_text

about = {
    "website": 'https://lemmy.ml/',
    "wikidata_id": 'Q84777032',
    "official_api_documentation": "https://join-lemmy.org/api/",
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}
paging = True
categories = ['general', 'social media']

base_url = "https://lemmy.ml/"
"""By default, https://lemmy.ml is used for providing the results.  If you want
to use a different lemmy instance, you can specify ``base_url``.
"""

lemmy_type = "Communities"
"""Any of ``Communities``, ``Users``, ``Posts``, ``Comments``"""


def request(query, params):
    args = {
        'q': query,
        'page': params['pageno'],
        'type_': lemmy_type,
    }

    params['url'] = f"{base_url}api/v3/search?{urlencode(args)}"
    return params


def _format_content(content):
    html = MarkdownIt("commonmark", {"typographer": True}).enable(["replacements", "smartquotes"]).render(content)
    return html_to_text(html)


def _get_communities(json):
    results = []

    for result in json["communities"]:
        results.append(
            {
                'url': result['community']['actor_id'],
                'title': result['community']['title'],
                'content': _format_content(result['community'].get('description', '')),
            }
        )

    return results


def _get_users(json):
    results = []

    for result in json["users"]:
        results.append(
            {
                'url': result['person']['actor_id'],
                'title': result['person']['name'],
                'content': _format_content(result['person'].get('bio', '')),
            }
        )

    return results


def _get_posts(json):
    results = []

    for result in json["posts"]:
        results.append(
            {
                'url': result['post']['ap_id'],
                'title': result['post']['name'],
                'content': _format_content(result['post'].get('body', '')),
            }
        )

    return results


def _get_comments(json):
    results = []

    for result in json["comments"]:
        results.append(
            {
                'url': result['comment']['ap_id'],
                'title': result['post']['name'],
                'content': _format_content(result['comment']['content']),
            }
        )

    return results


def response(resp):
    json = resp.json()

    if lemmy_type == "Communities":
        return _get_communities(json)

    if lemmy_type == "Users":
        return _get_users(json)

    if lemmy_type == "Posts":
        return _get_posts(json)

    if lemmy_type == "Comments":
        return _get_comments(json)

    raise ValueError(f"Unsupported lemmy type: {lemmy_type}")
