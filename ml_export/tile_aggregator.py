import mercantile
from rio_tiler import main
import numpy as np
from affine import Affine
import rasterio
from rasterio.profiles import DefaultGTiffProfile
from ml_export import tile_generator
from ml_export.tile_class_generator import TileClassDataset
import logging
from tqdm import tqdm
from torch.utils.data import DataLoader

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


def calculate_webmercator_meters_per_pixel(zoom_level):
    """Calculate webmercator pixel size based on zoom level."""
    meters_per_pixel = 20037508 * 2 / 2 ** (8 + zoom_level)
    return meters_per_pixel


def calculate_zoom_tile_transform(zoom_level, tile_object,
                                  tile_creation_buffer=250):
    """Make Affine transform for GeoTIFF.

    Arguments
    ---------
    zoom_level : int
        Destination zoom level.
    tile_object : :py:class:`mercantile.Tile`
        Tile object to get GeoTIFF transform for.
    tile_creation_buffer : int, optional
        Buffer to add to the boundaries of the tile in pixel units. Defaults to
        ``250``.

    Returns
    -------
    transform, width, height tuple
    transform : :py:class:`affine.Affine`
        Affine transformation to convert GeoTIFF.
    width : float
        width of the tile in pixel units with `tile_creation_buffer` added to
        both sides.
    height : float
        height of the tile in pixel units with `tile_creation_buffer` added to
        both top and bottom.
    """

    # Calculate Pixel Size Based on desired end tile_level
    meters_per_pixel = calculate_webmercator_meters_per_pixel(zoom_level)

    # Calculate XY BBox in meters of tile_object
    bbox_xy = mercantile.xy_bounds(tile_object)

    transform = Affine(meters_per_pixel, 0,
                       bbox_xy.left - tile_creation_buffer, 0,
                       -meters_per_pixel, bbox_xy.top + tile_creation_buffer)
    height = int((bbox_xy.top - bbox_xy.bottom) / meters_per_pixel)
    width = int((bbox_xy.right - bbox_xy.left) / meters_per_pixel)

    # print(height)
    # print(width)

    return transform, width + tile_creation_buffer * 2, height + tile_creation_buffer * 2


def create_webmercator_cog_profile(tile_object, zoom_level, num_channels,
                                   dtype=np.uint8, tile_creation_buffer=250):
    """Create WebMercator cog_profile for output.

    Uses :py:class:`rasterio.profiles.DefaultGTiffProfile` to generate a cloud-
    optimized GeoTIFF profile for the imagery.

    Arguments
    ---------
    tile_object : :py:class:`mercantile.Tile`
        tile object to create COG profile for.
    zoom_level : int
        zoom level integer for the COG profile.
    num_channels : int
        Number of channels to indicate in the COG profile.
    dtype : dtype, optional
        Value format for imagery. Defaults to ``np.uint8``.
    tile_creation_buffer : int, optional
        Pixel size of the buffer to use when generating the
        :py:class:`affine.Affine` object for the tile during COG profile
        generation. Defaults to 250.

    """

    transform, width, height = calculate_zoom_tile_transform(
        zoom_level=zoom_level, tile_object=tile_object,
        tile_creation_buffer=tile_creation_buffer)
    cog_profile = DefaultGTiffProfile(count=num_channels, height=height,
                                      width=width, crs="EPSG:3857",
                                      transform=transform, dtype=dtype)
    cog_profile.update({"driver": "GTiff", "interleave": "pixel",
                        "tiled": True, "blockxsize": 512,
                        "blockysize": 512, "compress": "LZW"})

    return cog_profile


def build_cog_from_tiles(file_name, large_tile_object,
                         raster_tile_server_template,
                         desired_small_tile_zoom_level=17,
                         desired_super_res_tile_zoom_level=19, cog=False,
                         indexes=None, tile_size=256):
    """Create a Cloud-Optimized GeoTIFF from tiles.

    This function doesn't return anything, but writes a COG dataset to
    `file_name`.

    Arguments
    ---------
    file_name : str
        Path to save the COG.
    large_tile_object : :py:class:`mercantile.Tile`
        Tile object to generate a COG from.
    raster_tile_server_template : str
        Path to a raster tileserver that can provide raster data for the new
        COG.
    desired_small_tile_zoom_level : int, optional
        Small tile zoom level for the COG. Defaults to ``17``.
    desired_super_res_tile_zoom_level : int, optional
        Desired maximum resolution zoom level for the COG. Defaults to ``19``.
    cog : bool, optional
        Is the data source targeted by `raster_tile_server_template` a COG?
        Defaults to ``False`` (no).
    indexes : list of ints, optional
        Indexes of RGB channels in the raster imagery. If not provided,
        defaults to ``[1, 2, 3]`` for COGs, which is altered to ``[0, 1, 2]``
        for non-COG image sources.
    tile_size : int, optional
        Length of a tile edge in pixels. Defaults to ``256``.

    Returns
    -------
    Nothing

    """

    if indexes is None:
        indexes = [1, 2, 3]
        num_channels = len(indexes)
    else:
        num_channels = len(indexes)

    large_cog_profile = create_webmercator_cog_profile(
        large_tile_object, desired_super_res_tile_zoom_level,
        num_channels=num_channels)

    with rasterio.open(file_name, 'w', **large_cog_profile) as dst_dataset:

        stol, _ = tile_generator.create_super_tile_list(
            large_tile_object,
            desired_zoom_level=desired_small_tile_zoom_level)

        for small_tile_object in tqdm(stol):
            super_res_tile = tile_generator.create_super_tile_image(
                small_tile_object, raster_tile_server_template,
                desired_zoom_level=desired_super_res_tile_zoom_level,
                indexes=indexes, tile_size=tile_size, cog=cog)
            left, bottom, right, top = mercantile.xy_bounds(*small_tile_object)
            dst_window = rasterio.windows.from_bounds(
                left, bottom, right, top,
                transform=large_cog_profile['transform'])

            dst_dataset.write(
                super_res_tile.astype(large_cog_profile['dtype']),
                window=dst_window)


def build_cog_from_tiles_gen(file_name, large_tile_object,
                             raster_tile_server_template,
                             desired_small_tile_zoom_level=17,
                             desired_super_res_tile_zoom_level=19, cog=False,
                             indexes=None, tile_size=256, batch_size=4,
                             num_workers=4,
                             tile_dataset_class=TileClassDataset,
                             detection_module=None):
    """Create a Cloud-Optimized GeoTIFF from a tile generator instance.

    Arguments
    ---------
    file_name : str
        Path to save the COG to.
    large_tile_object : :py:class:`mercantile.Tile`
        Tile object to generate a COG from.
    raster_tile_server_template : str
        Path to a raster tileserver that can provide raster data for the new
        COG.
    desired_small_tile_zoom_level : int, optional
        Small tile zoom level for the COG. Defaults to ``17``.
    desired_super_res_tile_zoom_level : int, optional
        Desired maximum resolution zoom level for the COG. Defaults to ``19``.
    cog : bool, optional
        Is the data source targeted by `raster_tile_server_template` a COG?
        Defaults to ``False`` (no).
    indexes : list of ints, optional
        Indexes of RGB channels in the raster imagery. If not provided,
        defaults to ``[1, 2, 3]`` for COGs, which is altered to ``[0, 1, 2]``
        for non-COG image sources.
    tile_size : int, optional
        Length of a tile edge in pixels. Defaults to ``256``.
    batch_size : int, optional
        Number of tiles to pull into a worker at a time. Defaults to ``4``.
    num_workers : int, optional
        Number of workers to create to build the COG at once. Defaults to
        ``4``.
    tile_dataset_class : `TileClassDataset` or `OpenCVClassDataset`, optional
        Class of the dataset to use to generate the COG. Defaults to
        `TileClassDataset`, in some cases it may be preferable to use an
        `OpenCVClassDataset`.
    detection_module : ``None`` or `MLModel` or `MLTFServing` inst., optional
        During COG creation, inference can be run to create a ML output layer.
        To do so, pass an instantiated model of type `MLModel` or `MLTFServing`
        in this argument.

    Returns
    -------
    file_name : str
        Path to the generated COG.

    """
    if indexes is None:
        indexes = [1, 2, 3]
        num_channels = len(indexes)
    else:
        num_channels = len(indexes)

    if detection_module is not None:
        num_channels = detection_module.num_channels

    large_cog_profile = create_webmercator_cog_profile(
        large_tile_object, desired_super_res_tile_zoom_level,
        num_channels=num_channels, dtype=np.float32)

    with rasterio.open(file_name, 'w', **large_cog_profile) as dst_dataset:

        tile_dataset = tile_dataset_class(
            root_tile_obj=large_tile_object,
            raster_location=raster_tile_server_template,
            desired_zoom_level=desired_small_tile_zoom_level,
            super_res_zoom_level=desired_super_res_tile_zoom_level, cog=cog,
            tile_size=tile_size, indexes=indexes
            )
        # uses the PyTorch DataLoader to iterate over tiles in the dataset
        tile_iterator = DataLoader(tile_dataset, batch_size=batch_size,
                                   shuffle=False, num_workers=num_workers)

        for super_res_tile_batch, small_tile_obj_batch in tqdm(tile_iterator):
            super_res_tile_np = super_res_tile_batch.numpy()
            if detection_module is not None:
                super_res_tile_results = detection_module.predict_batch(
                    super_res_tile_batch.numpy())
            else:
                super_res_tile_results = super_res_tile_np
            for super_res_tile, small_tile_object_tensor in zip(
                    super_res_tile_results, zip(small_tile_obj_batch[i].numpy()
                                                for i in range(batch_size))):
                left, bottom, right, top = small_tile_object_tensor

                dst_window = rasterio.windows.from_bounds(
                    left, bottom, right, top,
                    transform=large_cog_profile['transform'])
                dst_dataset.write(super_res_tile.astype(
                    large_cog_profile['dtype']), window=dst_window)

    return file_name
