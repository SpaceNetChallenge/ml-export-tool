from shapely import geometry
import mercantile
from rio_tiler import main
import numpy as np
import logging
import requests

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)





def get_task_info(taskid, tasking_manager_api_endpoint='https://tasks.hotosm.org/api/v1'):


    r = requests.get('{}/project/{}?as_file=false'.format(tasking_manager_api_endpoint, taskid))


    task_dict = r.json()



    return task_dict

def get_task_area_from_task_dict(task_dict):

    aoi_geom = geometry.geo.asShape(task_dict['areaOfInterest'])


    return aoi_geom

def get_task_area_from_id(taskid, tasking_manager_api_endpoint='https://tasks.hotosm.org/api/v1'):


    task_dict = get_task_info(taskid, tasking_manager_api_endpoint=tasking_manager_api_endpoint)

    aoi_geom = get_task_area_from_task_dict(task_dict=task_dict)


    return aoi_geom

