from sagemaker_jupyter_server_extension.spark_history_server_utils import is_valid_s3_uri_dir


def test_is_valid_s3_uri_dir():
    # Test cases
    test_uris = [
        ('s3://amazon-datazone-v2-767398137313-us-west-2-206404586/dzd_bdz2brzyiqt8k0/b7ruw66l094u1c/dev/glue/b7ruw66l094u1c-42f50589-dc03-47b0-8a00-87c524ff2832/glue-spark-events-logs/', True),
        ('s3://my-bucket/path/to/directoryã/', True),
        ('s3://my-bucket', True),
        ('s3://my-bucket/', True),
        ('s3://my-bucket/path/', True),
        ('s3://my-bucket/path/to/directory/', True),
        ('s3://my-bucket-name/', True),
        ('s3://1234/', True),
        ('s3://my-bucket-123/some/path/', True),
        ('s3://my-bucket/directory with spaces/', True),
        ('s3://my-bucket/directory_with_underscores/', True),
        ('s3://my-bucket/directory-with-hyphens/', True),
        ('s3://my-bucket/path/to/file.txt', False),  # Invalid (not a directory)
        ('s3://a' * 63 + '/', False),  # Maximum length bucket name
        ('s3://a' * 64 + '/', False),  # Invalid (too long)
        ('s3://my_bucket/', False),  # Invalid (underscore)
        ('s3://My-Bucket/', False),  # Invalid (uppercase)
        ('s3://my-bucket-/', False),  # Invalid (ends with hyphen)
        ('s3://-my-bucket/', False),  # Invalid (starts with hyphen)
        ('s3://my.bucket/', False),  # Invalid (period)
        ('https://my-bucket.s3.amazonaws.com/', False),  # Invalid (not s3:// protocol)
        ('my-bucket/some/path/', False),  # Invalid (no s3:// protocol),
        ('s3://1234ã/', False) #Invalid (Non-ASCII Character bucket name)
    ]
    for uri, isValid in test_uris:
        assert is_valid_s3_uri_dir(uri) == isValid
