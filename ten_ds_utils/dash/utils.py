from urllib.parse import urlparse


def clean_pathname(pathname: str, prefix_url: str):
    """
    Removes the prefix_url from the pathname
    """
    return f"/{pathname[len(prefix_url):].strip('/')}"


def fetch_query_string(href: str) -> str:
    """
    Parses the href for any query string, returning it if found
    """
    return urlparse(href).query
