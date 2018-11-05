from shapely import geometry
import mercantile
from rio_tiler import main



def getTileList(geom,
                zoom=17):
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    geom: shapely geometry of area.

    west, south, east, north : sequence of float
        Bounding values in decimal degrees.
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

        tileGeom = geometry.shape(mercantile.feature(tile)['geometry'])

        if tileGeom.intersects(geom):

            tile_list.append(tile)


        return tile_list




def create_super_tile_list(tile_coord, zoomLevel=2):
    
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_coord: mercantile tile object


    zoom : int Zoom Level for Tiles
        One or more zoom levels.

    Returns
    ------
    tile_list: list of tile objects to gather
    tile_position_list: list of relative tile position
    """

    rel_tile_pos = np.asarray([(0,0), (0,1), (1,1), (1,0)])
    
    tile_list = [tile_coords]
    tile_position_list = [(0,0)]
    for zoom in range(zoomLevel):
        child_tile_list = []
        child_tile_position = []
        for tile, tile_pos in zip(tile_list, tile_position_list):
            
            tile_pos_np = np.asarray(tile_pos)
            print(tile_pos_np)
            print(tile_pos_np*2+rel_tile_pos)
            
            child_tile_list.extend(mercantile.children(tile))
            child_tile_position.extend(tile_pos_np*2+rel_tile_pos)

        tile_list = child_tile_list
        tile_position_list = child_tile_position
        print(child_tile_position)


    return tile_list, tile_position_list


def create_super_tile_image(tile_coord, zoomLevel=2,indexes=[1,2,3], tile_size=256):
    
    """Generate the Tile List for The Tasking List

    Parameters
    ----------
    tile_coord: mercantile tile object


    zoom : int Zoom Level for Tiles
        One or more zoom levels.

    Returns
    ------
    superResTile: returns numpy array of size (len(indexes,(2**zoomLevel)*tile_size,(2**zoomLevel)*tile_size)
    """
    
    tile_list, tile_position_list = create_super_tile_list(tile_coord, zoomLevel=2)
    
    superRestile = np.zeros((len(indexes,(2**zoomLevel)*tile_size,(2**zoomLevel)*tile_size),dtype=float)

    for tile_coords, (tilePlace_x, tilePlace_y) in zip(tileList, tile_position_list):
        tilePlaceCalc = [tilePlace_x*tile_size, (tilePlace_x+1)*tile_size, tilePlace_y*tile_size, (tilePlace_y+1)*tile_size]
        print([tilePlace_x*tile_size, (tilePlace_x+1)*tile_size, tilePlace_y*tile_size, (tilePlace_y+1)*tile_size])

        tmpTile, mask = main.tile(address,
                               tile_coords.x,
                               tile_coords.y,
                               tile_coords.z
                               )

        superRestile[:,tilePlaceCalc[0]:tilePlaceCalc[1],tilePlaceCalc[2]:tilePlaceCalc[3]]=tmpTile
        
    
    return superResTile





