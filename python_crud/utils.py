# utils
#

import os
import re
from urllib.parse import parse_qs
from json import loads, dumps


def tojson(items):
    res = []
    for r in items:
        res.append(loads(r))
    return res


def is_id(id_):
    return id_.isdigit() or is_uuid(id_)


def is_uuid(uuid_):
    """
    Check if uuid_to_test is a valid UUID using regex.

    Parameters
    ----------
    uuid_to_test : str
        The UUID string to check.

    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

    Examples
    --------
    >>> is_uuid('a2345678-1234-5678-1234-567812345678')
    True
    >>> is_uuid('g2345678-1234-5678-1234-567812345679') # Invalid UUID
    False
    """
    pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    return bool(pattern.match(uuid_))


def file_type(path):
    """Guess the MIME type of a file based on its extension."""
    extension = os.path.splitext(path)[1]
    if extension == '.html':
        return 'text/html'
    elif extension == '.css':
        return 'text/css'
    elif extension == '.js':
        return 'application/javascript'
    elif extension == '.ico':
        return 'image/vnd.microsoft.icon'
    elif extension in ('.png', '.jpg', '.jpeg', '.gif'):
        return 'image/' + extension[1:]
    else:
        return 'application/octet-stream'


def parse_post(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
        return None
    request_body = environ['wsgi.input'].read(request_body_size).decode()
    # return request_body
    return parse_qs(request_body)


def get_post_param(_from, _to):
    """Получим значения из массива переменных в переменные.
    !В случае отсутсвия переменной бросает AttributeError
    """
    for var in _from:
        getattr(_to, var)
        setattr(_to, var, _from[var][0])
