"""tests ml_export.tm_interface.base"""

import os
import pytest
## Note, for mac osx compatability import something from shapely.geometry before importing fiona or geopandas
## https://github.com/Toblerity/Shapely/issues/553  * Import shapely before rasterio or fioana
from shapely import geometry
import mercantile
from rio_tiler import main
import numpy as np
from ml_export import tile_generator, tm_interface
import logging
import rasterio
raster_address = "s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13_cloud.tiff"

PREFIX = os.path.join(os.path.dirname(__file__), 'fixtures')

mask_address = '{}/my-bucket/test_super_tile.tif'.format(PREFIX)
#tests/fixtures/my-bucket/test_super_tile.tif
with rasterio.open(mask_address) as src:
    super_tile_test = src.read()
    src_profile = src.profile


def test_import():
    print("Import Success")

def test_get_tasking_id_aoi():

    taskid = 5400

    aoi_geom = tm_interface.get_task_area_from_id(taskid=taskid)










