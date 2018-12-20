import geopandas as gpd
import rasterio
import rasterio.features
import rasterio.warp


def create_geojson(raster_name, geojson_name, threshold=0.5):
    """Binarize and vectorize a raster file.

    This function takes an image mask with float values between ``0`` and ``1``
    and converts it to a binary mask, which it then polygonizes. Use the
    `threshold` argument to set the mimimum pixel intensity value that will
    be included in the vectorized polygon outputs.

    Arguments
    ---------
    raster_name : str
        Path to the raster mask file to vectorize.
    geojson_name : str
        Desired output path for the geojson file.
    threshold : float, optional
        Minimum pixel intensity to include in the vectorized polygons. Defaults
        to ``0.5``.

    """
    geomList = []
    with rasterio.open(raster_name) as dataset:
        # Read the dataset's valid data mask as a ndarray.
        data = dataset.read()
        data[data >= threshold] = 1
        data[data < threshold] = 0
        mask = data == 1
        # Extract feature shapes and values from the array.
        for geom, val in rasterio.features.shapes(data, mask=mask,
                                                  transform=dataset.transform):
            # Transform shapes from the dataset's own coordinate
            # reference system to CRS84 (EPSG:4326).
            geom = rasterio.warp.transform_geom(
                dataset.crs, 'EPSG:4326', geom, precision=6)
            geomList.append(geom)
    gdf = gpd.GeoDataFrame(geometry=geomList)
    gdf.crs = {'init': 'epsg:4326'}
    gdf.to_file(geojson_name, driver="GeoJSON")

    return geojson_name
