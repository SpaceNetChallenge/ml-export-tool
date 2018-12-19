import boto3
import json
import tempfile


def create_stac_item(id,
                     geometry,
                     stac_properties,
                     stac_links,
                     stac_assets):
    stac_base = {
        "id": id,
        "type": "Feature",
        "geometry": geometry,
        "properties": stac_properties,
        "links": stac_links,
        "assets": stac_assets
    }

    return stac_base


def build_stac_properties(datetime,
                          ml_algorithm,
                          derived_from,
                          title):
    stac_properties = {"datetime": datetime,
                       "title": title,
                       "ml:algorithm": ml_algorithm,
                       "derived_from": derived_from}

    return stac_properties


def build_stac_links(self_url,
                     derived_from_url,
                     root_catalog_url=None,
                     parent_catalog_url=None,
                     algorithm_collection_url=None):

    stac_links = [
        {"rel": "self",
         "href": self_url},
        {"rel": "derived_from",
         "href": derived_from_url,
        "title": "Inference Performed using this data"}
    ]


    if root_catalog_url is not None:
        stac_links.extend(
            [{"rel": "root",
              "href": root_catalog_url,
              "title": "Root Catalog"}]

        )

    if parent_catalog_url is not None:
        stac_links.extend(
            [{"rel": "parent",
              "href": parent_catalog_url,
              "title": "Parent Catalog"}]

        )

    if algorithm_collection_url is not None:
        stac_links.extend(
            [{"rel": "collection",
              "href": algorithm_collection_url,
              "title": "Algorithm Collection Details"}]

        )

    return stac_links

def build_stac_assets(raster_url, raster_binary_thresh, raster_mask_binary_url=None, geojson_url=None,
                      thumbnail_url=None,
                      object_type="building",
                      product_details_url=None
                      ):

    stac_assets = {"raster": {"href": raster_url,
                                   "title": "Segmentation Output",
                                   "binary_threshold": raster_binary_thresh,
                                   "object_type": object_type,
                              "type": "image/vnd.stac.geotiff; cloud-optimized=true"
                                   }
                   }


    if raster_mask_binary_url is not None:
        stac_assets["raster_mask"] = {"href": raster_mask_binary_url,
                                      "title": "Binary Segmentation Output",
                                      "object_type": object_type,
                                      "type": "image/vnd.stac.geotiff; cloud-optimized=true"
                                      }

    if geojson_url is not None:
        stac_assets["geojson"] = {"href": geojson_url,
                                      "title": "Vector Representation of output",
                                      "object_type": object_type,
                                  "type": "application/geo+json	"
                                      }

    if product_details_url is not None:
        stac_assets["product_details"] = {"href": product_details_url,
                                      "title": "Details about Algorithm used",
                                      "type": "application/pdf"
                                      }


    return stac_assets


def save_stac_item(stac_dict, stac_bucket, stac_key):


    s3 = boto3.client('s3')
    s3 = boto3.client('s3')

    with tempfile.NamedTemporaryFile(mode='w+') as tf:
        tfname = tf.name



        json.dump(stac_dict, tf)
        tf.seek(0)
        tf.flush()
        s3.upload_file(tfname, stac_bucket, stac_key)





