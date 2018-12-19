"""tests ml_export.tile_generator.base"""

import os
import pytest
## Note, for mac osx compatability import something from shapely.geometry before importing fiona or geopandas
## https://github.com/Toblerity/Shapely/issues/553  * Import shapely before rasterio or fioana
from shapely import geometry
import mercantile
from rio_tiler import main
import numpy as np
from ml_export import tile_generator
import logging
import rasterio


raster_tile_server = "https://tiles.openaerialmap.org/5ae36dd70b093000130afdd4/0/5ae36dd70b093000130afdd5/{z}/{x}/{y}.png"
raster_address = "s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13_cloud.tiff"

PREFIX = os.path.join(os.path.dirname(__file__), 'fixtures')

mask_address = '{}/my-bucket/test_super_tile.tif'.format(PREFIX)
#tests/fixtures/my-bucket/test_super_tile.tif
with rasterio.open(mask_address) as src:
    super_tile_test = src.read()
    src_profile = src.profile

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def test_import():
    print("Import Success")

def test_super_res():


    tile_coord = mercantile.tile(-115.24, 36.1986, 17)


    super_res_tile = tile_generator.create_super_tile_image(tile_coord,
                                                            address=raster_address,
                                                            desired_zoom_level=19,
                                                            indexes=[1],
                                                            cog=True)


    #TODO build better 3 channel test
    np.testing.assert_allclose(super_res_tile.astype(int)
                               , super_tile_test[None,0,:,:].astype(int))



def test_super_res_tms():

    tile_coord = mercantile.tile(39.299515932798386, -6.080908028740757, 17)

    super_res_tile = tile_generator.create_super_tile_image(tile_coord,
                                                            address=raster_tile_server,
                                                            desired_zoom_level=19,
                                                            indexes=[1,2,3],
                                                            cog=False)






#