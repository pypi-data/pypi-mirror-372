from urllib.parse import urlparse


class S3URI:
    """
    Simplified version of https://stackoverflow.com/questions/42641315/s3-urls-get-bucket-name-and-path
    """

    def __init__(self, uri: str):
        self.parsed_url = urlparse(uri, allow_fragments=False)

    @property
    def bucket(self):
        return self.parsed_url.netloc

    @property
    def key(self):
        return self.parsed_url.path.lstrip("/")

    @property
    def url(self):
        return self.parsed_url.geturl()
