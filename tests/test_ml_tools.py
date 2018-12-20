import os
import pytest
## Note, for mac osx compatability import something from shapely.geometry before importing fiona or geopandas
## https://github.com/Toblerity/Shapely/issues/553  * Import shapely before rasterio or fioana
from shapely import geometry
import mercantile
from rio_tiler import main
import numpy as np
from ml_export import tile_generator, tm_interface
from ml_export.ml_tools import mlbase
import logging
import rasterio



model_dictionary = '{"model_file": "test.hdf5", "model_description": "Passthrough Model", "model_version": "0.1", "model_speed": 20}' #  # numpy arrays per second
#raster_address = "s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13_cloud.tiff"
raster_address = "s3://spacenet-dataset/AOI_2_Vegas/srcData/rasterData/AOI_2_Vegas_MUL-PanSharpen_Cloud.tif"




test_np_array = np.zeros((3,1024,1024))
test_np_array_list = [test_np_array, test_np_array, test_np_array]



def test_ml_model():

    testmodel = mlbase.MLModel(model_dictionary)

    predict_result = testmodel.predict(test_np_array)

    predict_batch_result = testmodel.predict_batch(test_np_array_list)

    assert predict_result.shape == (1,1024,1024)

    assert len(predict_batch_result) == 3

    assert predict_batch_result[0].shape == (1,1024,1024)


def test_ml_model_tiles():

    tile_coord = mercantile.tile(-115.24, 36.1986, 17)
    super_res_tile = tile_generator.create_super_tile_image(tile_coord,
                                                            address=raster_address,
                                                            desired_zoom_level=19,
                                                            indexes=[1])

    testmodel = mlbase.MLModel(model_dictionary)

    predict_result = testmodel.predict(super_res_tile)

    predict_batch_result = testmodel.predict_batch([super_res_tile, super_res_tile, super_res_tile])

    assert predict_result.shape == (1,1024,1024)

    assert len(predict_batch_result) == 3

    assert predict_batch_result[0].shape == (1,1024,1024)
