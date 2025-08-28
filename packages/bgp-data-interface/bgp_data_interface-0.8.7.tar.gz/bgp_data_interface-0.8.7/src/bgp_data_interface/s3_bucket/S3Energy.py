import boto3
from botocore.exceptions import ClientError
import io
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.service_resource import Bucket
import pandas as pd



DEFAULT_BUCKET_NAME = 'bgp-energy-data'
DEFAULT_CLOUD = 'AWS'
DEFAULT_SITE = 'DUMMY'
DEFAULT_FORECAST = 'solar'
DEFAULT_STATE = 'collected'
DEFAULT_FILE = 'dummy.csv'



class S3Energy:

    s3_client: S3Client
    bucket: Bucket
    bucket_name: str


    def __init__(self,
            access_key: str,
            secret_key: str,
            bucket_name: str) -> None:

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.s3_client = session.client('s3')
        self.bucket_name = bucket_name

        s3_resource = session.resource('s3')
        self.bucket = s3_resource.Bucket(bucket_name)



    def retrieve_csv(self, key: str) -> pd.DataFrame:

        if not self.exists(key):
            return pd.DataFrame()

        obj = self.bucket.Object(key)
        body = obj.get()["Body"]
        csv = body.read().decode('utf-8')

        return pd.read_csv(io.StringIO(csv), index_col=False)



    def retrieve_excel(self, key: str) -> dict[str, pd.DataFrame]:

        if not self.exists(key):
            return {}

        obj = self.bucket.Object(key)
        body = obj.get()["Body"]
        excel = body.read()

        return pd.read_excel(io.BytesIO(excel), engine='openpyxl', sheet_name=None)



    def download(self, key: str, destination: str) -> None:

        self.bucket.download_file(key, destination)



    def store_csv(self, df: pd.DataFrame, key: str) -> None:

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        self.bucket.put_object(
            Key=key,
            Body=csv_buffer.getvalue(),
            ContentType='application/csv')



    def upload(self, key: str, source: str) -> None:
        
        self.bucket.upload_file(source, key)



    def exists(self, key: str) -> bool:

        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            return False

        return True
