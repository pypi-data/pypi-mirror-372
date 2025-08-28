import os, boto3, uuid
from simple_blogger.generator import File

class S3Uploader():
    def __init__(self, key_id=None, secret=None, bucket=None, endpoint='https://storage.yandexcloud.net'):
        key_id = key_id or os.environ.get('S3_KEY_ID')
        secret = secret or os.environ.get('S3_SECRET')
        self.bucket = bucket or os.environ.get('S3_BUCKET')
        self.client = boto3.client("s3"
                            , aws_access_key_id=key_id
                            , aws_secret_access_key=secret
                            , endpoint_url=endpoint)

    def upload(self, file:File):
        file_name = str(uuid.uuid4())
        self.client.upload_fileobj(file.get_file(), self.bucket, file_name, ExtraArgs={ 'ContentType': file.get_content_type() })
        return self.client.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': self.bucket, 'Key': file_name })