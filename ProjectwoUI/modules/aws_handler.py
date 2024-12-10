import boto3
import requests
import numpy as np
import cv2

class AWSHandler:
    """Handles interaction with AWS S3."""
    def __init__(self, aws_access_key, aws_secret_access_key, region_name):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def list_all_buckets(self):
        response = self.s3.list_buckets()
        return [bucket['Name'] for bucket in response['Buckets']]

    def list_objects_in_bucket(self, bucket_name):
        paginator = self.s3.get_paginator('list_objects_v2')
        object_urls = []
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                for obj in page['Contents']:
                    object_key = obj['Key']
                    object_urls.append(f"https://{bucket_name}.s3.amazonaws.com/{object_key}")
        return object_urls
