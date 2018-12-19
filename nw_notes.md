## Notes on `ml_export/ml_tools/mlbase.py`
This module appears to be intended for loading in ML models. It contains two classes:
- `mlmodel`: Load in an .hdf5-formatted, trained model file and perform inference. Methods:
    - `init`: initialize logging and run `self.load_model_dict` to load in the model.
    - `load_model_dict`: Load model into memory based on the provided dict. The dict should contain 4 elements:
        - `'model_file'`: The path to the .hdf5-formatted model
        - `'model_description'`: A short text description of the model
        - `'model_version'`
        - `'model_speed'`: A numeric indication of the number of seconds it takes to evaluate a numpy array.
        - All this function does is call `json.loads` on the `model_json_string` passed during `__init__`.
    - `estimate_time` (uses self.model_dict['model_speed'] and an argument `tiles_length`)
    - `predict`: Run inference, __TODO: not currently implemented__, returns a 4D array of shape `[None, 1, input_y, input_x]`
    - `predict_batch`: takes a list of numpy arrays and (should) run them through `predict`. __TODO: Not currently implemented.__
- `ml_tf_serving`
    - essentially the same as `mlmodel` above. Only difference is that at this point, the method `predict_batch` is partially implemented.
    - `predict_batch`: run prediction through multiple queries to the prediction API.
    - Steps:
        1. It takes in a batch of tiles (called "super_res_tile_batch", which I think means they're higher-resolution than the input tile resolution passed by the user) and creates a list out of them
        2. Uses the `requests` library to post to the prediction API. __It sends a list of images as the `json` argument of `requests.post()`, which I think might not work?__
        3. It uses the return from the `requests.post()` call, which it looks like has an element called `'outputs'` that contains the predictions. It expects these to be 256x256 numpy arrays.
        4. After reshaping the array it returns these `image_preds`.

## Notes on `ml_export/ml_tools/mlopencv.py`
This module appears to be intended for creating Torch datasets for OpenCV models.
- `mlopencv` function: I have no idea what this does.
- `OpenCVClassDataset` class: subclass of `torch.utils.data.Dataset`
  - Arguments:
    - root_tile_obj :
    - raster_location :
    - desired_zoom_level :
    - super_res_zoom_level :
    - cog : bool, optional
    - tile_size : int, optional
    - indexes : list of ints, optional. Defines the indices of the channels in the image to use for model inference (I think?)
  - Operations:
    1. uses `ml_export.tile_generator` to create a tile list from `root_tile_obj` at the desired zoom level. This produces two outputs, `small_tile_object_list` and `small_tile_position_list`.
  - methods:
    - `__getitem__`: Gets a tile image using `tile_generator.create_super_tile_image` at the super-resolved zoom level passed in `__init__`. Returns the tile i mage and its xy bounds obtained using `mercantile.xy_bounds`

## Notes on `ml_export/tile_generator.py`
- `get_tile_from_tms` function
  - arguments:
    - html_template : str, template URL to the TMS tileserver
    - tile_obj : ?
    - no_data : int, optional, value that represents missing data.
  - operations:
    1. queries the tileserver to get the image object.
    2. loads the image object from the request response and reshapes the array.
    3. returns the image.
- `get_tile_list` function
  - see documentation in the file
  - operations:
    1. creates `tiles` at desired zoom level using `mercantile.tiles`

## Notes on `ml_export/tm_interface.py`
- Implements API queries to get AOI geometry for a specific task from the TM API.

## Notes on `ml_export/utils.py`
- Utilities for generating overviews, managing S3 storage of imagery, and creating STAC items for inference outputs.
