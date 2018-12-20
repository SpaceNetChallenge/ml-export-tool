# Creating an ML-Export Tool 
[![Build Status](https://travis-ci.com/SpaceNetChallenge/ml-export-tool.svg?branch=dev)](https://travis-ci.com/SpaceNetChallenge/ml-export-tool)

## User Story

A user would like to perform machine learning against an area.  They provide an area and the service responds with 

    1. Available machine learning features for that area: i.e.
        * Building Count
        * Building Area
        * Building Shapes
    2. Estimated time to produce requested output
    3. Output formats for result.  


# Interface End Points

### GET
1. TMS
2. Vector Tiles
3. GeoJson
4. Cloud Optimized GeoTiff

### Push:
1. New ML Prediction
2. New STAC-ITEM 



## Storage Layer:
We will use the [Spatial Temporal Access Catalog Spec](https://github.com/radiantearth/stac-spec) for Storage Documentation 9
STAC-ITEMS:  Each machine learning output will be stored as an STAC ITEM.  Binary masks can be stored as a Cloud Optimized GeoTiff to encourage easy processing
        
    *   STAC-ITEMS can be added to Catalog Collections based on TaskID.  
    STAC-ITEMS produced by the ML Service should have at least 3 assets:
    
        *  results_cog
        *  results_cog_binary
        *  results_cog_geojson
    
    *   STAC-ITEMs for other apis can be documnted
        * [AI for Earth](https://github.com/Microsoft/AIforEarth-API-Development/blob/master/Quickstart.md)
         
    
    
### Why STAC:
*   STAC is an industry initiative to create a overarching, cloud native searchable catalog of geospatial data.  
*   Machine Learning outputs in mapping situations are Spatial and Temporal Items.
*   This will allow cumalitive machine learning results to queable and should allow flexibility as we add new types of data
*   An example of the SpaceNet STAC-Browser can be found at [SpaceNet-STAC](https://spacenet-stac.netlify.com/)
       
###


## Test items:

Test Location 1:
SpaceNet Area of Interest Las Vegas

##

## Demo Map:

https://cwnets-demo.netlify.com/#/url/s3%3A%2F%2Fspacenet-dataset%2FAOI_2_Vegas%2FsrcData%2FrasterData%2FAOI_2_Vegas_MUL-PanSharpen_Cloud.tif/center/-115.24685,36.19648/zoom/17
### srcImagery  
    * s3://spacenet-dataset/AOI_2_Vegas/srcData/rasterData/AOI_2_Vegas_MUL-PanSharpen_Cloud.tif
    * s3://spacenet-dataset/AOI_2_Vegas/srcData/rasterData/AOI_2_Vegas_PAN_Cloud.tif
    * s3://spacenet-dataset/AOI_2_Vegas/srcData/rasterData/AOI_2_Vegas_MUL_Cloud.tif 
    

### results COG:
    * s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13_cloud.tiff

### results GeoJSON:
    * s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13.geojson
 
### results MBtiles:
    * s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13.mbtiles


Example to pull tiles from COG GeoTIFF
```python
from rio_tiler import main
import mercantile

address = "s3://spacenet-dataset/AOI_2_Vegas/resultData/AOI_2_Vegas_MULPS_v13_cloud.tiff"


# -115.24, 36.1, -115.2, 36.2, 17)
tile_coords = mercantile.tile(-115.24, 36.1986, 18)

tile, mask = main.tile(address,
                           tile_coords.x,
                           tile_coords.y,
                           tile_coords.z
                           )

```






## Result Aggregator:

    1. Create ML-Tile List = 12*z19 Tile (1024pix x 1024 pix tiles) with 1 z19 tile overlap (25% overlap)
    2. Pass new ML-Tile to ML-Algorithm:
    3. Recieve ML-Algorithm output: 
        
        * PNG:    
            * Band 1: RasterTile_Building_Center
            * Band 2: RasterTile_Building_Edge (Optional)
        * Threshold_Point: (0,1)
        * VectorTile: (Vector Tile)
        
    4. Combine ML-Algorithm output:
        * Cloud Optimized GeoTiff
            Band 1: RasterTile_Building_Center
            Band 2: RasterTile_Building_Edge (Optional)
            GEOTIFF_TAG: Threshold_Value
        * GeoJSON
        * VectorTile: Z18
        * RasterTile: Z18


## ML-Algorithm:
    
    
    ## input: 
    * List of JSON: 
        [{'imageId': imageId,
         'imageLoc': https://bucket-in/z/x/y.png,
         'dst_raster':   https://bucket-out/z/x/y.png,
         'dst_vector':   {https://bucket-out/z/x/y.json,
         }] 
    
    image tile for imageLoc should return a:
    
        12 * z19 resolution (z17 scope): 
        
        |x-2,y-2|x-1,y-2|x+1,y-2|x+2,y-2|
        |x-2,y-1|x-1,y-1|x+1,y-1|x+2,y-1|
        |x-2,y+1|x-1,y+1|x+1,y+1|x+2,y+1|  = (1024x1024 pixel 3-Band png 8 bit jpeg) = Z18 x 4x SR Tile
        |x-2,y+2|x-1,y+2|x+1,y+1|x+2,y+2|

    ## output: 
    * 1024x1024  x 2 bands 
    
        Band 1: RasterTile_Building_Center
        Band 2: RasterTile_Building_Edge (Optional)
        GEOTIFF_TAG: Threshold_Value
    
    * 1024 x 1024 Vector Tile
    
    * geojson: Pixel Coordinates
     
    


## Key pieces of information for model to report
1. Estimated Time for Production {x seconds/tile}
2. Accuracy {Precision/Recall, Mean Error)
3. Resolution Required {zoomTile, GSD}
4. Output Resolution {zoomTile, GSD}
5. Features {'Building Count', 'Building Area', 'Building Bounding Box', 'Building Instance Segmentation'}
6. Region Trained: {STAC_Item}
7. Test Data:
8. src docker container



## Type of Requests (Tasking Manager to Service):

### Get Requests:
    * endpoint/getmodels
        * report registered models


    * endpoint/getmodelcapability/{modelname}
        * report key pieces above
        
    * endpoint/estimate/{modelname, geobox, datasource}
        * report estimated time of completion (Days/Hours/Minutes)
        * report estimated cost
        
    * endpoint/status/{processid}
        * report process status
        * report estimated completion
        
    * endpoint/orderexport/orderid/tms/{x}/{y}/{z}.png
    * endpoint/orderexport/orderid/vectortile/{x}/{y}/{z}.pbf
        
### Post Requests:

    * endpoint/orderexport/{modelversion, geobox, datasource}
        * return orderId for status
        

## Type of Request (Service to ML Model)
        
### Get Requests:

    * endpoint/{modelid}/{x}/{y}/{z}.pbf
        * return vector tile for specified model request
        
    * endpoint/{modelid}/{x}/{y}/{z}.png
        * return raster tile for specified model request
    
        
### Post Requests:
     * endpoint/{modeljson}}
        * register new model

