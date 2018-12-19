from shapely import geometry
import mercantile
from rio_tiler import main
import numpy as np
import logging
import requests
from PIL import Image
from io import BytesIO
import cv2
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)



def get_tile_from_tms(html_template, tile_obj, no_data=0):
#    html_template = "https://14ffxwyw5l.execute-api.us-east-1.amazonaws.com/production/tiles/{z}/{x}/{y}.jpg?url=s3://spacenet-dataset/AOI_2_Vegas/srcData/rasterData/AOI_2_Vegas_MUL-PanSharpen_Cloud.tif&rgb=5,3,2&linearStretch=true&band1=5&band2=7"



    if True: #try:
        r = requests.get(html_template.format(x=tile_obj.x, y=tile_obj.y, z=tile_obj.z), stream=True)

        if r.status_code == 200:

            image = np.array(Image.open(BytesIO(r.content)))

        else:
            image = np.full((256, 256, 3), fill_value=no_data)

    #except:
    #    image = np.full((256, 256, 3), fill_value=no_data)
    #    logging.error("timeout: {html}".format(html=html_template.format(x=tile_obj.x, y=tile_obj.y, z=tile_obj.z)))







    logging.debug(html_template.format(x=tile_obj.x, y=tile_obj.y, z=tile_obj.z))



    return image



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


def create_super_tile_list(tile_object, desired_zoom_level=19):
    ## TODO Implement Stopping at desired zoom_level
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_object: mercantile tile object


    desired_zoom_level : int Zoom Level For interior tiles ie This object should be built of z19 tiles.

    Returns
    ------
    tile_object_list: list of tile objects to gather
    tile_position_list: list of relative tile position
    """

    rel_tile_pos = np.asarray([(0, 0), (0, 1), (1, 1), (1, 0)])
    
    tile_object_list = [tile_object]
    tile_position_list = [(0, 0)]

    while tile_object_list[0].z < desired_zoom_level:

        child_tile_list = []
        child_tile_position = []
        for tile, tile_pos in zip(tile_object_list, tile_position_list):
            
            tile_pos_np = np.asarray(tile_pos)

            child_tile_list.extend(mercantile.children(tile))
            child_tile_position.extend(tile_pos_np*2+rel_tile_pos)

        tile_object_list = child_tile_list
        tile_position_list = child_tile_position
        
    return tile_object_list, tile_position_list


def create_super_tile_image(tile_object, address, desired_zoom_level=19, indexes=None, tile_size=256, cog=True):
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_object: mercantile tile object
    address: COG location
    desired_zoom_level : int Zoom Level For interior tiles ie This object should be built of z19 tiles.

    indexes: List of indexes for address.  This is incase it is more than 3-bands
    tile_size: int tile_size for query.  Standard is 256, 256



    Returns
    ------
    super_restile: returns numpy array of size (len(indexes,(2**zoom_level)*tile_size,(2**zoom_level)*tile_size)
    """

    if cog:
        return create_super_tile_image_cog(tile_object, address, desired_zoom_level=desired_zoom_level, indexes=indexes, tile_size=tile_size)

    else:

        return create_super_tile_image_tms(tile_object, address, desired_zoom_level=desired_zoom_level, indexes=indexes, tile_size=tile_size)




def create_super_tile_image_cog(tile_object, address, desired_zoom_level=19, indexes=None, tile_size=256):

    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_object: mercantile tile object
    address: COG location
    desired_zoom_level : int Zoom Level For interior tiles ie This object should be built of z19 tiles.

    indexes: List of indexes for address.  This is incase it is more than 3-bands
    tile_size: int tile_size for query.  Standard is 256, 256



    Returns
    ------
    super_restile: returns numpy array of size (len(indexes,(2**zoom_level)*tile_size,(2**zoom_level)*tile_size)
    """

    if indexes is None:
        indexes = [1, 2, 3]
    
    tile_object_list, tile_position_list = create_super_tile_list(tile_object, desired_zoom_level=desired_zoom_level)

    zoom_level = tile_object_list[0].z - tile_object.z
    super_tile_size = int((2 ** zoom_level) * tile_size)
    super_restile = np.zeros(
        (len(indexes), super_tile_size, super_tile_size),
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
                                   tile_coords.z,
                                   indexes=indexes
                                   )

        super_restile[:, tile_place_calc[0]:tile_place_calc[1], tile_place_calc[2]:tile_place_calc[3]] = tmp_tile
        
    return super_restile


def create_super_tile_image_tms(tile_object, html_template, desired_zoom_level=19, indexes=None, tile_size=256):
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_object: mercantile tile object
    html_template: COG location
    desired_zoom_level : int Zoom Level For interior tiles ie This object should be built of z19 tiles.

    indexes: List of indexes for address.  This is incase it is more than 3-bands
    tile_size: int tile_size for query.  Standard is 256, 256



    Returns
    ------
    super_restile: returns numpy array of size (len(indexes,(2**zoom_level)*tile_size,(2**zoom_level)*tile_size)
    """

    if indexes is None:
        indexes = [1, 2, 3]
    # Shift indexes to be zero rated
    indexes = list(np.asarray(indexes)-1)

    tile_object_list, tile_position_list = create_super_tile_list(tile_object, desired_zoom_level=desired_zoom_level)

    zoom_level = tile_object_list[0].z - tile_object.z
    super_tile_size = int((2 ** zoom_level) * tile_size)

    super_restile = np.zeros(
        (len(indexes), super_tile_size, super_tile_size),
        dtype=float
    )

    for tile_coords, (tilePlace_x, tilePlace_y) in zip(tile_object_list, tile_position_list):
        tile_place_calc = [
            tilePlace_x * tile_size,
            (tilePlace_x + 1) * tile_size,
            tilePlace_y * tile_size,
            (tilePlace_y + 1) * tile_size
        ]

        # print
        logging.debug(tile_place_calc)

        tmp_tile = get_tile_from_tms(html_template, tile_coords)

        if tmp_tile.shape[0] == 512:
            tmp_tile = cv2.resize(tmp_tile, (256,256), interpolation=cv2.INTER_CUBIC)

        if tmp_tile.shape[2] > len(indexes):
            tmp_tile = tmp_tile[:,:, indexes]


        super_restile[:, tile_place_calc[0]:tile_place_calc[1], tile_place_calc[2]:tile_place_calc[3]] = np.moveaxis(tmp_tile, 2, 0)

    return super_restile
