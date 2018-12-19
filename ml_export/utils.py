import rasterio
from rasterio.enums import Resampling
import boto3
import json


# create overviews
def create_overview(file_name, factors=None):
    if factors is None:
        factors = [2, 4, 8, 16]

    with rasterio.open(file_name, 'r+') as dst:
        dst.build_overviews(factors, Resampling.average)
        dst.update_tags(ns='rio_overview', resampling='average')
        dst.update_tags(ns='OVR_RESAMPLING_ALG', resampling='average')

    return file_name


# build s3 http
def build_s3_http(bucket_name, key, region='us-east-1'):

    http_loc = "http://{bucket_name}.s3.amazonaws.com/{key}".format(bucket_name=bucket_name, key=key)

    return http_loc


# upload to s3
def upload_to_s3(file_name, bucket_name, key):

    s3 = boto3.client('s3')
    s3.upload_file(file_name, bucket_name, key)


    return build_s3_http(bucket_name, key)


# upload to s3 stac
def create_stac_item(s3_path,
                     raster_src,
                     api_location):
    s3_dict = {"raster_inference": s3_path,
               "raster_source": raster_src,
               "ml_api_location": api_location
               }

    return json.dumps(s3_dict)

