import rasterio
from rasterio.enums import Resampling
import boto3
import json


# create overviews (low-res versions of dataset to speed rendering)
def create_overview(file_name, factors=None):
    """Create low-resolution overviews of file for quick rendering.

    Arguments
    ---------
    file_name : str
        File to be rendered.
    factors : list of ints, optional
        Degrees of downsampling for overviews. Defaults to [2, 4, 8, 16] if
        not provided.

    Returns
    -------
    file_name : str
        The filename passed to `create_overview`. The overviews are saved
        within the file.

    """
    if factors is None:
        factors = [2, 4, 8, 16]

    with rasterio.open(file_name, 'r+') as dst:
        dst.build_overviews(factors, Resampling.average)
        dst.update_tags(ns='rio_overview', resampling='average')
        dst.update_tags(ns='OVR_RESAMPLING_ALG', resampling='average')
        dst.close()

    return file_name


def build_s3_http(bucket_name, key, region='us-east-1'):
    """Build URL to S3 bucket."""
    http_loc = "http://{bucket_name}.s3.amazonaws.com/{key}".format(
        bucket_name=bucket_name, key=key)
    return http_loc


def upload_to_s3(file_name, bucket_name, key):
    """Upload file to S3 bucket. Returns URL to the bucket."""
    s3 = boto3.client('s3')
    s3.upload_file(file_name, bucket_name, key)
    return build_s3_http(bucket_name, key)


def create_stac_item(s3_path, raster_src, api_location):
    """Create a STAC .json for an ML inference output stored on S3."""
    s3_dict = {"raster_inference": s3_path,
               "raster_source": raster_src,
               "ml_api_location": api_location
               }
    return json.dumps(s3_dict)
