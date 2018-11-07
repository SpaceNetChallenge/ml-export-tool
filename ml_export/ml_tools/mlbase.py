import logging
import numpy as np
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)






class mlmodel():


    """mlmodel test case
    The ml model base class should have 4 functions

    init:
    load_model_dict: This should Load The model into memory based on the provided model dictionary
    predict:  This should receive a np array of 3 x 1024 x 1024 and return a numpy array of 1x1024x1024
    predict_batch:  This should receive a list of np arrays of [np(3,1024,1024)] and return a list of [np(1,1024,1024]


    """


    def __init__(self, model_dict, debug=False):
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
        self.model_dict = model_dict

        ## Load Model Into Memory
        self.load_model_dict(model_dict)




    def load_model_dict(self, model_dict):

        pass



    def predict(self, np_array):

        return np.zeros((1,1024,1024))



    def predict_batch(self, list_np_array):

        list_np_array_results = []
        for np_array in list_np_array:

            list_np_array_results.append(np.zeros((1,1024,1024)))


        return list_np_array_results




        return list_np_array




