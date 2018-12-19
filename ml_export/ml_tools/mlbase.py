import logging
import numpy as np
import json
import requests
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)








class mlmodel():


    """mlmodel test case
    The ml model base class should have 4 functions

    init:
    load_model_dict: This should Load The model into memory based on the provided model dictionary
    predict:  This should receive a np array of 3 x 1024 x 1024 and return a numpy array of 1x1024x1024
    predict_batch:  This should receive a list of np arrays of [np(3,1024,1024)] and return a list of [np(1,1024,1024]


    model_dictionary = {'model_file': "test.hdf5",
                "model_description": "Passthrough Model",
                "model_version": "0.1",
                "model_speed": 20,   # numpy arrays per second
                                    }



    """


    def __init__(self, model_json_string, debug=False):
        ''' Inititiate model '''

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Create the Handler for logging data to a file
        logger_handler = logging.StreamHandler()
        # Create a Formatter for formatting the log messages
        logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

        # Add the Formatter to the Handler
        logger_handler.setFormatter(logger_formatter)

        # Add the Handler to the Logger

        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        self.logger.addHandler(logger_handler)


        ## Assign Model Dictionary
        self.model_json = model_json_string

        ## Load Model Into Memory
        self.load_model_dict()


    def estimate_time(self, tiles_length):
        """Returns Completion estimate in Seconds"""


        return self.model_dict['model_speed']* tiles_length


    def load_model_dict(self):


        self.model_dict = json.loads(self.model_json)



    def predict(self, np_array):

        return np_array[None, 0, :, :]



    def predict_batch(self, list_np_array):

        list_np_array_results = []
        for np_array in list_np_array:

            list_np_array_results.append(np_array[None,0, :, :])


        return list_np_array_results




class ml_tf_serving():


    """mlmodel test case
    The ml model base class should have 4 functions

    init:
    load_model_dict: This should Load The model into memory based on the provided model dictionary
    predict:  This should receive a np array of 3 x 1024 x 1024 and return a numpy array of 1x1024x1024
    predict_batch:  This should receive a list of np arrays of [np(3,1024,1024)] and return a list of [np(1,1024,1024]


    model_dictionary = {'model_file': "test.hdf5",
                "model_description": "Passthrough Model",
                "model_version": "0.1",
                "model_speed": 20,   # numpy arrays per second
                                    }



    """


    def __init__(self, api_location, output_num_channels=1, debug=False):
        ''' Inititiate model '''

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Create the Handler for logging data to a file
        logger_handler = logging.StreamHandler()
        # Create a Formatter for formatting the log messages
        logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

        # Add the Formatter to the Handler
        logger_handler.setFormatter(logger_formatter)

        # Add the Handler to the Logger

        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        self.logger.addHandler(logger_handler)


        ## Assign Model Dictionary
        self.predict_api_loc = api_location
        self.num_channels = output_num_channels
        self.model_speed = 1

        ## Load Model Into Memory
        self.load_model_dict()


    def estimate_time(self, tiles_length):
        """Returns Completion estimate in Seconds"""


        return self.model_speed * tiles_length


    def load_model_dict(self):

        return 0


    def predict(self, np_array):

        return np_array[None, 0, :, :]



    def predict_batch(self, super_res_tile_batch):

        inputs = np.moveaxis(super_res_tile_batch, 1, 3).astype(np.float32) / 255


        payload = {'inputs': inputs.tolist()}

        # Send prediction request
        r = requests.post(self.predict_api_loc,
                          json=payload)
        content = json.loads(r.content)

        all_image_preds = np.asarray(content['outputs']).reshape(len(inputs), 256, 256)
        all_image_preds = all_image_preds[:, np.newaxis, :, :]

        return all_image_preds







