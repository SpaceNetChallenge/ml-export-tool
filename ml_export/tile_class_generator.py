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
    """A tile dataset generator built around `torch.utils.data.Dataset`."""
    def __init__(self, root_tile_obj, raster_location, desired_zoom_level,
                 super_res_zoom_level, cog=True, tile_size=256, indexes=None):
        """Initialize a `TileClassDataset` instance.

        Arguments
        ---------
        root_tile_obj :
        raster_location :
        desired_zoom_level : int
        super_res_zoom_level : int
        cog : bool, optional
            Is the image a cloud-optimized GeoTIFF? Defaults to yes (``True``).
        tile_size : int, optional
            Length of a tile edge in pixels. Defaults to ``256``.
        indexes : list of ints, optional
            The indexes of the RGB channels in the rasterio dataset. If not
            provided, defaults to ``[1, 2, 3]``, which is re-scaled to
            ``[0, 1, 2]`` if ``cog == False``.

        Returns
        -------
        An instance of `TileClassDataset` with the super-resolved tile
        ``mercantile.tile``s and tile indices defined for feeding into a model.

        """
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

        stol, stpl = tile_generator.create_super_tile_list(
            root_tile_obj, desired_zoom_level=desired_zoom_level)
        self.small_tile_object_list = stol
        self.small_tile_position_list = stpl

    def __len__(self):
        return len(self.small_tile_object_list)

    def __getitem__(self, idx):
        """Get a single ``(mercantile.tile, mercantile.xy_bounds)`` pair. """
        super_res_tile = tile_generator.create_super_tile_image(
            self.small_tile_object_list[idx], self.raster_location,
            desired_zoom_level=self.super_res_zoom_level, indexes=self.indexes,
            tile_size=self.tile_size, cog=self.cog)

        return super_res_tile, mercantile.xy_bounds(
            *self.small_tile_object_list[idx])
