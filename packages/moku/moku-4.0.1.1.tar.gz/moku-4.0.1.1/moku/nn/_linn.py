"""

Author: Aaron - Aqacia Pty Ltd for Liquid Instruments
        Alex Mason - Liquid Instruments
Date: 2024
"""

import json
import sys
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import logging
from typing import Any, Optional, List, Tuple
from copy import copy, deepcopy

# list of supported activations
_AVAILABLE_ACTIVATIONS = ["relu", "tanh", "sigmoid", "softsign", "linear"]
_LOG = logging.getLogger("Linn")


def list_activations():
    """
    List the available activation functions
    :return: List of available activation functions
    """
    return _AVAILABLE_ACTIVATIONS


class WeightClip(keras.constraints.Constraint):

    def __init__(self, clip_value: float = 1.0) -> None:
        """
        Clips all the weights/biases to be within the range [-1, 1] to help with quantization later on.
        :param clip_value: value to clip the model between (float).
        """
        super().__init__()
        self.clip_value = float(clip_value)

    def __call__(self, w: Any):
        """
        Clip the weights/biases to the symmetric bounds
        :param w: Tensor or variable representing the weights
        :return: Tensor or variable clipped to the bounds
        """
        return tf.clip_by_value(w, -self.clip_value, self.clip_value)

    def get_config(self):
        return {"name": self.__class__.__name__, "clip_value": self.clip_value}


class OutputClipLayer(keras.layers.Layer):
    def __init__(self, clip_value: float = 1.0):
        """
        Class for clipping the output layers of the network. Ensures that outputs are clipped to [-1, 1] bounds for
        quantization.
        """
        super().__init__()
        self.clip_value = float(clip_value)

    def call(self, inputs, *args, **kwargs):
        """
        Clip the inputs to the symmetric bounds
        :param inputs: The output of the previous layer
        :param args: Mirrored from base layer class.
        :param kwargs: Mirrored from base layer class.
        :return: Tensor or variable clipped to the bounds
        """
        return tf.clip_by_value(inputs, -self.clip_value, self.clip_value)


class LinnModel:
    def __init__(self):
        self.model = None
        self.training_inputs = None
        self.training_outputs = None

        self._input_transform_args = None
        self._output_transform_args = None

        self.model_definition = None

    def construct_model(
        self,
        layer_definition: list = None,
        show_summary: bool = False,
        optimizer: any = "adam",
        loss: any = "mse",
        metrics: any = (),
    ) -> None:
        """
        Construct the model to be used by the rest of the functions in this class.
        :param layer_definition: a list of tuples of the form `(layer_width, activation)` 
        which defines the model. If not provided the default model will be used. 
        `(layer_width,)` can be used to signify a linear (identity) activation function.
        :param show_summary: (bool) determines whether the model summary is displayed
        :param optimizer: optimizer fed to the keras compile option.
        :param loss: loss function fed to the keras compile option.
        :param metrics: metrics for the model to track during training
        :return: None
        """

        # check the input and output
        if self.training_inputs is None or self.training_outputs is None:
            raise TypeError("Please set the training data first.")

        # check the model definition type
        if layer_definition is not None:
            if type(layer_definition) is not list:
                raise TypeError(
                    f"Expected type:<list> for model definition. Received: <{type(layer_definition)}>."
                )
            elif len(layer_definition) == 0:
                raise ValueError("layer_definition can't be empty.")
        else:
            raise ValueError("layer_definition can't be empty.")

        # assign the definition for checking
        self.model_definition = layer_definition

        # construct the model
        input_layer = keras.layers.Input((self.training_inputs.shape[-1],))
        prev_layer = input_layer
        # prev_layer = None
        for idx, layer_defn in enumerate(layer_definition):
            if type(layer_defn) is not tuple:
                raise TypeError(
                    f"layer_definition index:{idx} is type:<{type(layer_defn)} not <tuple>."
                )

            if len(layer_defn) != 2:
                raise ValueError(
                    f"layer_definition index:{idx} should have length 2, not {len(layer_defn)}."
                )

            # grab the activation function
            # activation = 'linear'

            activation = str(layer_defn[1])
            if activation not in list_activations():
                raise ValueError(
                    f"Activation {activation} is not in the list of supported activations. "
                    f"Try {list_activations()}."
                )
            # grab the layer width
            try:
                layer_width = int(layer_defn[0])
            except ValueError as e:
                raise ValueError(f"Error converting the layer width: {e.args}.")

            prev_layer = keras.layers.Dense(
                layer_width,
                activation=activation,
                kernel_constraint=WeightClip(),
                bias_constraint=WeightClip(),
            )(prev_layer)
            prev_layer = OutputClipLayer()(prev_layer)

        # compile the model for training
        self.model = keras.Model(input_layer, prev_layer)
        self.model.compile(
            optimizer=optimizer, loss=loss, metrics=[met for met in metrics]
        )

        # summarize if necessary
        if show_summary:
            self.model.summary()


    def _check_model_definition(self):
        # Check the input_layer first
        if type(self.model_definition[0]) is not tuple:
            _LOG.warning(
                f"Definition of input_layer is type:<{type(self.model_definition[0])} not <tuple>."
            )

        if len(self.model_definition[0]) != 1:
            _LOG.warning(
                f"Definition of input_layer should have length 1, not {len(self.model_definition[0])}."
            )

        if len(self.model_definition[0]) == 2:
            _LOG.warning(f"Ignored the activation function in the input_layer")

        if self.model_definition[0][0] != self.training_inputs.shape[-1]:
            _LOG.warning(
                f"Shape of layer_definition index: 0 not match the shape of input data, should be "
                f"{self.training_inputs.shape[-1]}, not {self.model_definition[0][0]}. Changed to the shape of"
                f" input data automatically."
            )

        self.model_definition[0] = (self.training_inputs.shape[-1],)

        for idx, layer_defn in enumerate(self.model_definition[1:]):
            if type(layer_defn) is not tuple:
                raise TypeError(
                    f"layer_definition index:{idx+1} is type:<{type(layer_defn)} not <tuple>."
                )

            if len(layer_defn) not in [1, 2]:
                raise ValueError(
                    f"layer_definition index:{idx+1} should have length 1 or 2, not {len(layer_defn)}."
                )

            if len(layer_defn) == 2:
                if layer_defn[1] not in list_activations():
                    raise ValueError(
                        f"Activation {layer_defn[1]} is not in the list of supported activations. "
                        f"Try {list_activations()}."
                    )

        if self.model_definition[-1][0] != self.training_outputs.shape[-1]:
            _LOG.warning(
                f"Shape of layer_definition index: {len(self.model_definition)-1} does not match the shape of "
                f"output data, should be {self.training_outputs.shape[1:]}, not "
                f"{self.model_definition[-1][0]}. Changed to the shape of output data automatically"
            )
            if len(self.model_definition[-1]) == 2:
                self.model_definition[-1] = (
                    self.training_outputs.shape[-1],
                    self.model_definition[-1][1],
                )
            else:
                self.model_definition[-1] = (self.training_outputs.shape[-1],)

        return True

    def _check_data_model_dim(
        self, inputs: np.ndarray, outputs: np.ndarray, data_name: str
    ):
        """
        Check the data and model dimensions against one another to make sure they are correct.
        :param inputs: Inputs to the model
        :param outputs: Outputs of the model
        :param data_name: String indicating whether it's training or validation.
        :return: Boolean indicating whether everything is ok
        """
        # warn the user dimension checking is skipped
        if self.model is None:
            _LOG.warning(
                "Keras model is not initialized. Dimension checking will be skipped."
            )
            return False

        # check if the dimensions match the defined model
        if (
            len(inputs.shape) != len(self.model.input_shape)
            or inputs.shape[1:] != self.model.input_shape[1:]
        ):
            raise ValueError(
                f"Dimensions of {data_name} inputs do not match model: {inputs.shape[1:]}, "
                f"{self.model.input_shape[1:]}"
            )

        if (
            len(outputs.shape) != len(self.model.output_shape)
            or outputs.shape[1:] != self.model.output_shape[1:]
        ):
            raise ValueError(
                f"Dimensions of {data_name} outputs do not match model: {outputs.shape[1:]}, "
                f"{self.model.output_shape[1:]}"
            )

        # if we got this far, success!
        return True

    def _transform(self, data_array: np.ndarray, is_input: bool):
        """
        Transform the data into a domain amenable for quantization.
        :param data_array: Data array to be transformed
        :param is_input: is it an input or output?
        :return: Return the transformed array
        """
        # copy the array so we don't modify the original
        output_array = np.copy(data_array)
        # get the scales if they are missing
        if is_input and self._input_transform_args is None:
            self._input_transform_args = (
                np.min(output_array, axis=0),
                np.max(output_array, axis=0),
            )
        if not is_input and self._output_transform_args is None:
            self._output_transform_args = (
                np.min(output_array, axis=0),
                np.max(output_array, axis=0),
            )

        # scale everything according to the transform arguments
        if is_input:
            output_array -= self._input_transform_args[0]
            output_array /= (
                self._input_transform_args[1] - self._input_transform_args[0]
            )
        else:
            output_array -= self._output_transform_args[0]
            output_array /= (
                self._output_transform_args[1] - self._output_transform_args[0]
            )
        output_array = 2 * (output_array - 0.5)

        return output_array

    def _inverse_transform(self, data_array: np.ndarray, is_input: bool):
        """
        Undo the scaling of the transform function to bring data back to the original domain.
        :param data_array: Data to be transformed
        :param is_input: is it the input or output
        :return: Return the transformed array
        """
        # copy the array so we don't destroy the original
        output_array = np.copy(data_array)
        # see if things can be transformed
        if is_input and self._input_transform_args is None:
            raise RuntimeError(
                "Cannot inverse transform before first calling transform."
            )
        if not is_input and self._output_transform_args is None:
            raise RuntimeError(
                "Cannot inverse transform before first calling transform."
            )

        # perform the inverse scaling
        output_array /= 2.0
        output_array += 0.5
        if is_input:
            output_array *= (
                self._input_transform_args[1] - self._input_transform_args[0]
            )
            output_array += self._input_transform_args[0]
        else:
            output_array *= (
                self._output_transform_args[1] - self._output_transform_args[0]
            )
            output_array += self._output_transform_args[0]

        return output_array

    def set_training_data(
        self,
        training_inputs: np.ndarray,
        training_outputs: np.ndarray,
        scale: bool = True,
        input_data_boundary: Tuple[list] = None,
        output_data_boundary: Tuple[list] = None,
    ):
        """
        Set the training data to be used by the model and automatically scale them to use the full dynamic range if
        specified. Scaling will ensure the model inputs and outputs are in the domain [-1, 1]. Call this before
        constructing a model to assign the data dimensions in construction.
        :param training_inputs: numpy.ndarray of input training data which should match the model dimensions
        :param training_outputs: numpy.ndarray of output training data which should match the model dimensions
        :param scale: (bool) automatically scale the data to fit in the bounds.
        :param input_data_boundary: tuple of the input data boundaries that should be used for scaling
        :param output_data_boundary: tuple of the output data boundaries that should be used for scaling
        :return: None
        """

        # We copy the input data so the scaling doesn't affect the original. This can be big, so might
        # want to revisit and e.g. only copy if we're scaling
        training_inputs = np.array(copy(training_inputs), dtype=float)
        training_outputs = np.array(copy(training_outputs), dtype=float)

        if not scale and (
            input_data_boundary is not None or output_data_boundary is not None
        ):
            _LOG.warning(f"scale = False. Ignoring the boundary setting")

        if scale:
            if input_data_boundary is not None:
                if (
                    not isinstance(input_data_boundary, (list, tuple))
                    or len(input_data_boundary) != 2
                ):
                    raise TypeError(
                        "Expected tuple of the form (lower_bound, upper_bound) for boundary setting."
                    )

                if not isinstance(input_data_boundary[0], (np.ndarray, list)):
                    raise TypeError(
                        f"Lower bounds should be type:<numpy.ndarray> or type:<list> not {type(input_data_boundary[0])}."
                    )

                if not isinstance(input_data_boundary[1], (np.ndarray, list)):
                    raise TypeError(
                        f"Upper bounds should be type:<numpy.ndarray> or type:<list> not {type(input_data_boundary[1])}."
                    )

                if len(input_data_boundary[0]) != training_inputs.shape[-1]:
                    raise ValueError(
                        f"Dimensions of lower bounds do not match input: {len(input_data_boundary[0])}, "
                        f"{training_inputs.shape[-1]}"
                    )
                if len(input_data_boundary[1]) != training_inputs.shape[-1]:
                    raise ValueError(
                        f"Dimensions of upper bounds do not match input: {len(input_data_boundary[1])}, "
                        f"{training_inputs.shape[-1]}"
                    )

            if output_data_boundary is not None:
                if (
                    not isinstance(output_data_boundary, (list, tuple))
                    or len(output_data_boundary) != 2
                ):
                    raise TypeError(
                        "Expected tuple of the form (lower_bound, upper_bound) for boundary setting."
                    )

                if not isinstance(output_data_boundary[0], (np.ndarray, list)):
                    raise TypeError(
                        f"Lower bounds should be type:<numpy.ndarray> or type:<list> not {type(output_data_boundary[0])}."
                    )

                if not isinstance(output_data_boundary[1], (np.ndarray, list)):
                    raise TypeError(
                        f"Upper bounds should be type:<numpy.ndarray> or type:<list> not {type(output_data_boundary[1])}."
                    )

                if len(output_data_boundary[0]) != training_outputs.shape[-1]:
                    raise ValueError(
                        f"Dimensions of lower bounds do not match outputs: {len(input_data_boundary[0])}, "
                        f"{training_outputs.shape[-1]}"
                    )
                if len(output_data_boundary[1]) != training_outputs.shape[-1]:
                    raise ValueError(
                        f"Dimensions of upper bounds do not match outputs: {len(output_data_boundary[1])}, "
                        f"{training_outputs.shape[-1]}"
                    )

        if input_data_boundary is not None:
            self._input_transform_args = [
                np.array(boundary) for boundary in input_data_boundary
            ]
        if output_data_boundary is not None:
            self._output_transform_args = [
                np.array(boundary) for boundary in output_data_boundary
            ]

        # scale the data if necessary to scale the full dynamic range
        if scale:
            training_inputs = self._transform(training_inputs, True)
            training_outputs = self._transform(training_outputs, False)

        # set the internal variables
        self.training_inputs = training_inputs
        self.training_outputs = training_outputs

    @staticmethod
    def _log_missing_value(key: str, default_value: Any, config: dict):
        """
        Convenience function for informing the user they have failed to provide a value and the defaul will be used.
        :param key: Key associated with the lookup.
        :param default_value: default value that is being used.
        :param config: dictionary to be read from
        :return: value corresponding to the default or dictionary value
        """
        dict_value = config.get(key, None)
        if dict_value is None:
            _LOG.warning(f"Value for {key} missing. Using default:{default_value}.")
            return default_value
        else:
            return dict_value

    def fit_model(
        self,
        epochs: int,
        es_config: Optional[dict] = None,
        validation_split: float = 0.0,
        validation_data: Optional[tuple] = None,
        **keras_kwargs: Optional[Any],
    ):
        """
        Fit the model according to the data that is stored in the training inputs and outputs. 
        set_training_data and construct_model must be called prior to calling Model.fit_model()
        :param epochs: (int) number of epochs to train for
        :param es_config: configuration dictionary for the early stopping callback
        :param validation_split: (float) used to define the validation split
        :param validation_data: validation data in a tuple of form (inputs, outputs)
        :param keras_kwargs: keyword args to pass to the keras `fit` function
        :return: history object from the keras `fit` function
        """

        # cast to an integer or throw an error
        epochs = int(epochs)

        validation_split = float(validation_split)
        if validation_split < 0.0 or validation_split > 1.0:
            _LOG.warning("Validation split outside of bounds - coercing value.")
            validation_split = np.clip(validation_split, 0.0, 1.0)

        # check the validation data
        if validation_data is not None:
            if type(validation_data) is not tuple or len(validation_data) != 2:
                raise TypeError(
                    "Expected tuple of the form (val_input, val_output) for validation data."
                )

            if type(validation_data[0]) is not np.ndarray:
                raise TypeError(
                    f"Validation input should be type:<numpy.ndarray> not <{type(validation_data[0])}>."
                )

            if type(validation_data[1]) is not np.ndarray:
                raise TypeError(
                    f"Validation output should be type:<numpy.ndarray> not <{type(validation_data[1])}>."
                )

            # check the data dimensions
            success = self._check_data_model_dim(
                validation_data[0], validation_data[1], "validation"
            )
            if not success:
                raise RuntimeError(
                    f"Model is not initialized. Call {self.__class__.__name__}.construct_model to create"
                    f" the model."
                )

        # warn of a redundancy
        if validation_split > 0.0 and (validation_data is not None):
            _LOG.warning(f"Supplied validation_data overrides validation_split.")

        # callbacks to use
        callbacks = []

        # build the early stopping call back
        if es_config is not None:
            # make sure it's a dictionary
            if type(es_config) is not dict:
                raise TypeError(
                    f"Expected type:<dict> for early stopping configuration, not <{type(es_config)}>."
                )

            # parameters for the callback
            monitor = self._log_missing_value("monitor", "val_loss", es_config)
            patience = self._log_missing_value("patience", 5, es_config)
            restore = self._log_missing_value("restore", False, es_config)

            # callback to be used later
            es_callback = keras.callbacks.EarlyStopping(
                monitor=monitor,
                min_delta=0,
                patience=patience,
                verbose=0,
                mode="auto",
                baseline=None,
                restore_best_weights=restore,
            )
            callbacks.append(es_callback)

            # fail if there is no validation, yet we monitor it.
            if (
                validation_split == 0.0
                and validation_data is None
                and monitor == "val_loss"
            ):
                raise RuntimeError(
                    "Cannot monitor val_loss for early stopping with val_split=0.0 and val_data=None."
                )

        # finally fit the model
        if validation_data is not None:
            history = self.model.fit(
                self.training_inputs,
                self.training_outputs,
                epochs=epochs,
                validation_data=validation_data,
                callbacks=callbacks,
                **keras_kwargs,
            )
        else:
            history = self.model.fit(
                self.training_inputs,
                self.training_outputs,
                epochs=epochs,
                validation_split=validation_split,
                callbacks=callbacks,
                **keras_kwargs,
            )

        return history

    def predict(
        self,
        inputs: np.ndarray,
        scale: Optional[bool] = None,
        unscale_output: Optional[bool] = None,
        **keras_kwargs: Optional[Any],
    ):
        """
        Generates model predictions for given inputs, with optional scaling based on training settings.
        :param inputs: The input data to be run through the model
        :param scale: Whether the data should be scaled at the input. Scaling will ensure the model inputs are 
        scaled as set in set_training_data and `scale = None` will scale data if trained with scaling.
        :param unscale_output: Whether the data should be unscaled at the output. Unscaling will ensure the model 
        outputs are scaled as set in set_training_data and `unscale = None` will unscale data if trained with unscaling.
        :param keras_kwargs: parameters to be passed to the keras predict function if needed.
        :return: The model predictions
        """

        # Default input and output scaling to whatever was used in training
        if scale is None:
            scale = self._input_transform_args is not None

        if unscale_output is None:
            unscale_output = self._output_transform_args is not None

        if scale:
            inputs = self._transform(inputs, True)

        # call the prediction
        outputs = self.model.predict(inputs, **keras_kwargs)

        # unscale if necessary
        if unscale_output:
            outputs = self._inverse_transform(outputs, is_input=False)

        return outputs


# LINN format conversion

def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


custom_objects = {"OutputClipLayer": OutputClipLayer, "WeightClip": WeightClip}


def convert_keras_to_linn(
    model: keras.models.Model, input_channels: int, output_channels: int, **kwargs
):
    dims: List[int] = []
    jlayers: List[dict] = []

    assert isinstance(
        model, (keras.Sequential, keras.Model, LinnModel)
    ), f"Unsupported model {type(model)}"

    if isinstance(model, LinnModel):
        model = model.model

    colDepth = 0
    hardwareLayers = 0

    for i, layer in enumerate(model.layers):
        if isinstance(layer, (WeightClip, OutputClipLayer, keras.layers.InputLayer)):
            _eprint(f"Skipping layer {i} with type {type(layer)}")
            continue

        if isinstance(layer, keras.layers.InputLayer):
            assert i == 0, "Input layer must be first layer"
            inputs = layer.batch_shape[0]
            dims.append(inputs)
            _eprint(f"Input shape {inputs}")
        else:

            assert isinstance(
                layer, keras.layers.Dense
            ), f"Only Dense layers supported, got ({type(layer)})"

            layerWeights = layer.get_weights()
            assert len(layerWeights) == 2, "Layer must only contains weights and biases"

            # layers are stored in column-major order
            weights = layerWeights[0].transpose()
            bias = layerWeights[1]

            assert len(weights.shape) == 2, "Only two dimensional layers supported"
            assert len(bias.shape) == 1, "Biases must be a vector"

            nRows = weights.shape[0]
            nCols = weights.shape[1]
            nBias = bias.shape[0]

            assert 0 < nBias <= 100, "Number of output rows must be 100 or fewer"
            assert nBias == nRows, "Weights output does not match bias vector size"
            if hardwareLayers == 0:
                # Handle the input to the network
                assert 1 <= nCols <= 100, "Maximum network input size is 100"
                dims.append(nCols)
            else:
                assert nCols == dims[-1], (
                    f"Input size {nCols} does not match output "
                    f"of previous layer {dims[-1]}"
                )
            dims.append(nRows)

            # Ensure that the total number of weights and biases is not too large
            # to fit into the memory for each neuron.
            colDepth += nCols + 3  # bias
            hardwareLayers += 1

            jlayers.append(
                {
                    "activation": layer.activation.__name__.lower(),
                    "weights": weights.tolist(),
                    "biases": bias.tolist(),
                }
            )

    assert hardwareLayers <= 5, "Only five dense layers allowed"

    assert colDepth <= 1024, (
        "Total number of weights and biases too large,"
        "sum(L[0].shape[1] for L in layers) + 3*len(layers)"
        f" = {colDepth} must be <= 1024"
    )

    _eprint(f"Network latency approx. {colDepth} cycles")

    if "output_mapping" in kwargs:
        output_map = kwargs.get("output_mapping")
        prev_final_weights = deepcopy(jlayers[-1]["weights"])
        prev_final_bias = deepcopy(jlayers[-1]["biases"])
        assert isinstance(output_map, list), "Output mapping must be a list"
        assert len(output_map) <= len(prev_final_weights), (
            f"Output mapping must have less than {len(prev_final_weights)} elements"
        )
        assert len(output_map) > 0, "Output mapping must have at least one element"

        jlayers[-1]["weights"] = [[0] * len(prev_final_weights[0])] * len(output_map)
        jlayers[-1]["biases"] = [0] * len(output_map)

        for i, output_index in enumerate(output_map):
            assert isinstance(output_index, int), "Output mapping must be a list of integers"
            assert 0 <= output_index < len(prev_final_weights), "Output mapping must be in range of output size"
            jlayers[-1]["weights"][i] = prev_final_weights[output_index]
            jlayers[-1]["biases"][i] = prev_final_bias[output_index]

    # Attempt to pretty print in a more readable form than json.dump; weights
    # will print as a 2D grid instead of a linear list of lists
    assert len(dims) > 1

    if len(jlayers[0]["weights"][0]) > 4:
        assert (
            input_channels == 1
        ), "Only one channel is supported for > 4 network inputs"
    else:
        assert (
            input_channels == 1 or input_channels == len(jlayers[0]["weights"][0])
        ), f"Input channels must match input size {len(jlayers[0]['weights'][0])}"

    if len(jlayers[-1]["weights"]) > 4:
        assert (
            output_channels == 1
        ), "Only one channel is supported for > 4 network outputs"
    else:
        assert (
            output_channels == 1 or output_channels == len(jlayers[-1]["weights"])
        ), f"Output channels must match output size {len(jlayers[-1]['weights'])}"

    return {
        "version": "0.1",
        "num_input_channels": input_channels,
        "num_output_channels": output_channels,
        "layers": jlayers,
    }


def get_linn(
    model: keras.models.Model, input_channels: int, output_channels: int, **kwargs
) -> dict:
    """
    Converts a 'LinnModel' into the '.linn' format required for execution on the 
    Moku Neural Network Instrument. This function will also work with compatible 
    Keras models if configured according to 'LinnModel' standards.

    Args:
        model (keras.models.Model): The 'LinnModel' instance or a compatible Keras model.
        input_channels: An integer of the number of instrument inputs to connect to the network.
                        Determines processing mode (serial or parallel) based on the ratio between 
                        'input_channels' and the number of input neurons in the model.
        output_channels: An integer of the number of instrument outputs to connect to the network.
                        Determines processing mode (serial or parallel) based on the ratio between 
                        'output_channels' and the number of output neurons in the model.
    Keyword Args (Optional):
        output_mapping (list): A list of integers that selects which output neurons
                               should be used as the final output of the network.

    Returns:
        dict: The .linn JSON document or a dict of the network parameters suitable for loading in to the Neural Network instrument.
    """
    return convert_keras_to_linn(
        model=model, input_channels=input_channels, output_channels=output_channels, **kwargs
    )


def save_linn(
    model: keras.models.Model, input_channels: int, output_channels: int, file_name: str, **kwargs
):
    """
    Converts a Keras model which is suitable for execution on the Moku
    Neural Network Instrument into the `.linn` format and saves it to a
    file.

    Args:
        model (keras.models.Model): The 'LinnModel' instance or a compatible Keras model.
        input_channels: An integer of the number of instrument inputs to connect to the network.
                        Determines processing mode (serial or parallel) based on the ratio between 
                        'input_channels' and the number of input neurons in the model.
        output_channels: An integer of the number of instrument outputs to connect to the network.
                        Determines processing mode (serial or parallel) based on the ratio between 
                        'output_channels' and the number of output neurons in the model.
        file_name (str): Name of output .linn file, requires .linn extension.

    Keyword Args (Optional):
        output_mapping (list): A list of integers that selects which output neurons
                               should be used as the final output of the network.
    Returns:
        None. Saves the result to a .linn file for loading in to the Neural Network instrument.
    """

    linn_data = convert_keras_to_linn(
        model=model, input_channels=input_channels, output_channels=output_channels, **kwargs
    )
    with open(file_name, "w+") as _writer:
        json.dump(linn_data, _writer)
