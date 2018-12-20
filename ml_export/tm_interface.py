from shapely import geometry
import logging
import requests

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


def get_task_info(
        taskid,
        tasking_manager_api_endpoint='https://tasks.hotosm.org/api/v1'):
    """Get task metadata from the tasking manager API."""
    r = requests.get('{}/project/{}?as_file=false'.format(
        tasking_manager_api_endpoint, taskid))
    task_dict = r.json()
    return task_dict


def get_task_area_from_task_dict(task_dict):
    """Get AOI geometry as a shapely.geometry.shape from a TM task dict."""
    aoi_geom = geometry.geo.asShape(task_dict['areaOfInterest'])
    return aoi_geom


def get_task_area_from_id(
        taskid,
        tasking_manager_api_endpoint='https://tasks.hotosm.org/api/v1'):
    """Get AOI geometry from a task ID using the Tasking Manager API.

    Wraps `get_task_info` and `get_task_area_from_task_dict`.

    """
    task_dict = get_task_info(
        taskid, tasking_manager_api_endpoint=tasking_manager_api_endpoint)
    aoi_geom = get_task_area_from_task_dict(task_dict=task_dict)
    return aoi_geom
