from urllib.parse import urlparse


def extract_hostname(link: str) -> str:
    return urlparse(link).hostname
