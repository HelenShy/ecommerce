import boto
import re
import os
import boto3

from django.conf import settings
from boto3.session import Session


class AWSDownload(object):
    access_key = None
    secret_key = None
    bucket = None
    region = None
    expires = getattr(settings, 'AWS_DOWNLOAD_EXPIRE', 5000)

    def __init__(self,  access_key, secret_key, bucket, region, *args, **kwargs):
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        super(AWSDownload, self).__init__(*args, **kwargs)

    def get_filename(self, path, new_filename=None):
        current_filename =  os.path.basename(path)
        if new_filename is not None:
            filename, file_extension = os.path.splitext(current_filename)
            escaped_new_filename_base = re.sub(
                                            '[^A-Za-z0-9\#]+', 
                                            '-', 
                                            new_filename)
            escaped_filename = escaped_new_filename_base + file_extension
            return escaped_filename
        return current_filename

    def generate_url(self, path, download=True, new_filename=None):
        file_url = None
        filename = self.get_filename(path, new_filename=new_filename)
        session = boto3.Session(self.access_key, self.secret_key, region_name='eu-west-3')
        client = session.client( 's3', config= boto3.session.Config(signature_version='s3v4'))
        file_url = client.generate_presigned_url(
                                            'get_object', 
                                            Params = { 
                                                      'Bucket': self.bucket, 
                                                      'Key': path, 
                                                      'ResponseContentType': 'application/force-download',
                                                      'ResponseContentDisposition' : 'attachment;filename="%s"'%filename}, 
                                            ExpiresIn = self.expires,
                                                )
        return file_url