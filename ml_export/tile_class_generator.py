"""tests ml_export.tile_class_generator"""
import os
import pytest
## Note, for mac osx compatability import something from shapely.geometry before importing fiona or geopandas
## https://github.com/Toblerity/Shapely/issues/553  * Import shapely before rasterio or fioana
from shapely import geometry
import mercantile
from ml_export import tile_generator
from torch.utils.data import Dataset

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")


class TileClassDataset(Dataset):

    def __init__(self, root_tile_obj, raster_location,
                 desired_zoom_level, super_res_zoom_level,
                 cog=True,
                 tile_size=256,
                 indexes=None
                 ):

        self.root_tile_obj = root_tile_obj
        self.desired_zoom_level = desired_zoom_level
        self.super_res_zoom_level = super_res_zoom_level
        self.raster_location = raster_location
        self.cog = cog
        self.tile_size = tile_size

        if indexes is None:
            self.indexes = [1, 2, 3]
        else:
            self.indexes = indexes

        small_tile_object_list, small_tile_position_list = tile_generator.create_super_tile_list(root_tile_obj,
                                                                                                 desired_zoom_level=desired_zoom_level)
        self.small_tile_object_list = small_tile_object_list
        self.small_tile_position_list = small_tile_position_list

    def __len__(self):

        return len(self.small_tile_object_list)

    def __getitem__(self, idx):

        super_res_tile = tile_generator.create_super_tile_image(self.small_tile_object_list[idx],
                                                                self.raster_location,
                                                                desired_zoom_level=self.super_res_zoom_level,
                                                                indexes=self.indexes,
                                                                tile_size=self.tile_size,
                                                                cog=self.cog)

        return super_res_tile, mercantile.xy_bounds(*self.small_tile_object_list[idx])






