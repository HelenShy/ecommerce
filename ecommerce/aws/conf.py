import datetime
import os

AWS_GROUP_NAME = "AllWorldBooks_Group"
AWS_USERNAME = "AllWorldBooksUser"
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', "AKIAIPOSFSAOUHRESAHA")
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', "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")

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'ecommerce.aws.utils.MediaRootS3BototStorage'
STATICFILES_STORAGE = 'ecommerce.aws.utils.StaticRootS3BototStorage'
AWS_STORAGE_BUCKET_NAME = 'all-world-books'
S3DIRECT_REGION = 'us-east-2'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_month_later = datetime.date.today() + two_months
expires = date_two_month_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

PROTECTED_DIR_NAME = 'protected'
PROTECTED_MEDIA_URL = '//%s.s3.amazonaws.com/%s/' %( 
                    AWS_STORAGE_BUCKET_NAME,
                    PROTECTED_DIR_NAME)
AWS_DOWNLOAD_EXPIRE = 5000
