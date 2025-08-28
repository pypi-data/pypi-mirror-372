import boto3
from urllib.parse import urlunparse

BUCKET_URL_PREFIX = b'bucket:/'
"""Using a special scheme meant for objects in private buckets.

We do not use simply `s3://` because in this case the next segment
is usualy the bucket.
"""


def s3_client_bucket(repo, public=False):

    def s3_conf(subkey, boolean=False):
        get = repo.ui.configbool if boolean else repo.ui.config
        value = get(b'heptapod',
                    b'clone-bundles.s3.' + subkey.encode('ascii'))
        if boolean:
            return value
        elif value is not None:
            return value.decode('ascii')

    bucket_key = 'public-bucket' if public else 'private-bucket'
    scheme = 'https' if s3_conf('tls', boolean=True) else 'http'
    endpoint_url = urlunparse((scheme, s3_conf('endpoint'), '', '', '', ''))
    session = boto3.session.Session()
    client = session.client(
        service_name='s3',
        region_name=s3_conf('region'),
        endpoint_url=endpoint_url,
        aws_access_key_id=s3_conf('access_key'),
        aws_secret_access_key=s3_conf('secret_key'),
    )
    return client, s3_conf(bucket_key)
