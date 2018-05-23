from storages.backends.s3boto3 import S3Boto3Storage

StaticRootS3BototStorage = lambda: S3Boto3Storage (location='static')
MediaRootS3BototStorage = lambda: S3Boto3Storage (location='media')