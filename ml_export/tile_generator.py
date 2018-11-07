from shapely import geometry
import mercantile
from rio_tiler import main
import numpy as np
import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)





def get_tile_list(geom,
                  zoom=17):
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    geom: shapely geometry of area.

    zoom : int Zoom Level for Tiles
        One or more zoom levels.

    Yields
    ------
    list of tiles that intersect with

    """

    west, south, east, north = geom.bounds
    tiles = mercantile.tiles(west, south, east, north, zooms=zoom)
    tile_list = []

    for tile in tiles:

        tile_geom = geometry.shape(mercantile.feature(tile)['geometry'])

        if tile_geom.intersects(geom):

            tile_list.append(tile)

    return tile_list


def create_super_tile_list(tile_object, zoom_level=2):

    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_object: mercantile tile object


    zoom_level : int Zoom Level for Tiles
        One or more zoom levels to superres.

    Returns
    ------
    tile_object_list: list of tile objects to gather
    tile_position_list: list of relative tile position
    """

    rel_tile_pos = np.asarray([(0, 0), (0, 1), (1, 1), (1, 0)])
    
    tile_object_list = [tile_object]
    tile_position_list = [(0, 0)]
    for zoom in range(zoom_level):
        child_tile_list = []
        child_tile_position = []
        for tile, tile_pos in zip(tile_object_list, tile_position_list):
            
            tile_pos_np = np.asarray(tile_pos)
            print(tile_pos_np)
            print(tile_pos_np*2+rel_tile_pos)
            
            child_tile_list.extend(mercantile.children(tile))
            child_tile_position.extend(tile_pos_np*2+rel_tile_pos)

        tile_object_list = child_tile_list
        tile_position_list = child_tile_position
        
    return tile_object_list, tile_position_list


def create_super_tile_image(tile_object, address, zoom_level=2, indexes=None, tile_size=256):

    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_object: mercantile tile object
    address: COG location
    zoom_level : int Zoom Level for Tiles
        One or more zoom levels.
    indexes: List of indexes for address.  This is incase it is more than 3-bands
    tile_size: int tile_size for query.  Standard is 256, 256



    Returns
    ------
    super_restile: returns numpy array of size (len(indexes,(2**zoom_level)*tile_size,(2**zoom_level)*tile_size)
    """

    if indexes is None:
        indexes = [1, 2, 3]
    
    tile_object_list, tile_position_list = create_super_tile_list(tile_object, zoom_level=2)
    
    super_restile = np.zeros(
        (len(indexes), (2 ** zoom_level) * tile_size, (2 ** zoom_level) * tile_size),
        dtype=float
    )

    for tile_coords, (tilePlace_x, tilePlace_y) in zip(tile_object_list, tile_position_list):

        tile_place_calc = [
            tilePlace_x*tile_size,
            (tilePlace_x+1)*tile_size,
            tilePlace_y*tile_size,
            (tilePlace_y+1)*tile_size
        ]

        # print
        logging.debug(tile_place_calc)

        tmp_tile, mask = main.tile(address,
                                   tile_coords.x,
                                   tile_coords.y,
                                   tile_coords.z
                                   )

        super_restile[:, tile_place_calc[0]:tile_place_calc[1], tile_place_calc[2]:tile_place_calc[3]] = tmp_tile
        
    return super_restile
