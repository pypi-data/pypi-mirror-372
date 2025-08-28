import ctypes
import ctypes.util
from enum import IntEnum, auto
from importlib.resources import as_file, files
import sys
from typing import List, Sequence, TYPE_CHECKING, Union
import warnings

_use_numpy = False
if TYPE_CHECKING:
    import numpy as np
else:
    np = None


def enable_numpy() -> None:
    """
    Enables NumPy support. All arrays passed to this library must be NumPy
    arrays once this function is called. Also, all returned arrays are NumPy
    arrays once this function is called.

    This is the inverse function of `disable_numpy`.
    """

    global _use_numpy, np
    if np is not None:
        return
    import numpy as _np
    np = _np
    _use_numpy = True


def disable_numpy() -> None:
    """
    Disables NumPy support. All arrays passed to this library must be Python
    lists once this function is called. Also, all returned arrays are Python
    lists once this function is called.

    This is the inverse function of `enable_numpy`.
    You don't need to call this function if you didn't call `enable_numpy`
    beforehand. NumPy support is disabled by default.
    """

    global _use_numpy, np
    np = None
    _use_numpy = False


def _platform_libname():
    if sys.platform == "linux":
        return "libdnnets.so"
    elif sys.platform == "darwin":
        return "libdnnets.dylib"
    elif sys.platform == "win32":
        return "dnnets.dll"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def _load_shared_library():
    # Try loading the library bundled with the wheel
    try:
        p = files("dnnets._lib").joinpath(_platform_libname())
        with as_file(p) as f:
            return ctypes.CDLL(str(f))
    except (ModuleNotFoundError, OSError):
        pass

    # The package is likely installed through the system packgage manager then.
    # Try loading the system provided version of the library.
    lib_name = ctypes.util.find_library("dnnets")
    if lib_name is not None:
        return ctypes.CDLL(lib_name)

    raise RuntimeError("native dnnets implementation not found")


_dnnets_lib = _load_shared_library()


class _DnnetsResult(IntEnum):
    SUCCESS = 0
    UNSUPPORTED_LAYER_TYPE = auto()
    INCOMPLETE_NET = auto()
    MALFORMED_POLICY_DEFINITION = auto()
    WEIGHTS_BIASES_MISMATCH = auto()
    WRONG_NUMBER_OF_WEIGHTS = auto()
    WRONG_LAYER_SIZE = auto()
    MEMORY_LEAK = auto()
    FILE_NOT_FOUND = auto()
    OUT_OF_MEMORY = auto()
    SHARING_VIOLATION = auto()
    PATH_ALREADY_EXISTS = auto()
    ACCESS_DENIED = auto()
    PIPE_BUSY = auto()
    NO_DEVICE = auto()
    NAME_TOO_LONG = auto()
    INVALID_UTF8 = auto()
    INVALID_WTF8 = auto()
    BAD_PATH_NAME = auto()
    UNEXPECTED = auto()
    NETWORK_NOT_FOUND = auto()
    ANTIVIRUS_INTERFERENCE = auto()
    SYM_LINK_LOOP = auto()
    PROCESS_FD_QUOTA_EXCEEDED = auto()
    SYSTEM_FD_QUOTA_EXCEEDED = auto()
    SYSTEM_RESOURCES = auto()
    FILE_TOO_BIG = auto()
    IS_DIR = auto()
    NO_SPACE_LEFT = auto()
    NOT_DIR = auto()
    DEVICE_BUSY = auto()
    FILE_LOCKS_NOT_SUPPORTED = auto()
    FILE_BUSY = auto()
    WOULD_BLOCK = auto()
    PROCESS_NOT_FOUND = auto()
    OVERFLOW = auto()
    INVALID_CHARACTER = auto()
    UNEXPECTED_TOKEN = auto()
    INVALID_NUMBER = auto()
    INVALID_ENUM_TAG = auto()
    DUPLICATE_FIELD = auto()
    UNKNOWN_FIELD = auto()
    MISSING_FIELD = auto()
    LENGTH_MISMATCH = auto()
    SYNTAX_ERROR = auto()
    UNEXPECTED_END_OF_INPUT = auto()
    VALUE_TOO_LONG = auto()
    READ_FAILED = auto()
    END_OF_STREAM = auto()
    PERMISSION_DENIED = auto()


class _ModelDefinition(ctypes.Structure):
    pass


class _Model(ctypes.Structure):
    pass


class _Linear(ctypes.Structure):
    _fields_ = [("weights", ctypes.POINTER(ctypes.c_float)),
                ("biases", ctypes.POINTER(ctypes.c_float))]


class _LayerNorm(ctypes.Structure):
    _fields_ = [("weights", ctypes.POINTER(ctypes.c_float)),
                ("biases", ctypes.POINTER(ctypes.c_float)),
                ("eps", ctypes.c_float)]


class _Clip(ctypes.Structure):
    _fields_ = [("min", ctypes.c_float),
                ("max", ctypes.c_float)]


class _ELU(ctypes.Structure):
    _fields_ = [("alpha", ctypes.c_float)]


_dnnets_lib.dnnets_init.argtypes = []
_dnnets_lib.dnnets_init.restype = None

_dnnets_lib.dnnets_deinit.argtypes = []
_dnnets_lib.dnnets_deinit.restype = ctypes.c_uint32

_dnnets_lib.dnnets_new_model_definition.argtypes = [
    ctypes.POINTER(ctypes.POINTER(_ModelDefinition)), ctypes.c_uint32]
_dnnets_lib.dnnets_new_model_definition.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_linear.argtypes = [
    ctypes.POINTER(_ModelDefinition), _Linear, ctypes.c_uint32]
_dnnets_lib.dnnets_add_linear.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_layer_norm.argtypes = [
    ctypes.POINTER(_ModelDefinition), _LayerNorm, ctypes.c_uint32]
_dnnets_lib.dnnets_add_layer_norm.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_clip.argtypes = [
    ctypes.POINTER(_ModelDefinition), _Clip, ctypes.c_uint32]
_dnnets_lib.dnnets_add_clip.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_elu.argtypes = [
    ctypes.POINTER(_ModelDefinition), _ELU, ctypes.c_uint32]
_dnnets_lib.dnnets_add_elu.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_relu.argtypes = [
    ctypes.POINTER(_ModelDefinition), ctypes.c_uint32]
_dnnets_lib.dnnets_add_relu.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_relu6.argtypes = [
    ctypes.POINTER(_ModelDefinition), ctypes.c_uint32]
_dnnets_lib.dnnets_add_relu6.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_sigmoid.argtypes = [
    ctypes.POINTER(_ModelDefinition), ctypes.c_uint32]
_dnnets_lib.dnnets_add_sigmoid.restype = ctypes.c_uint32

_dnnets_lib.dnnets_add_tanh.argtypes = [
    ctypes.POINTER(_ModelDefinition), ctypes.c_uint32]
_dnnets_lib.dnnets_add_tanh.restype = ctypes.c_uint32

_dnnets_lib.dnnets_create.argtypes = [
    ctypes.POINTER(ctypes.POINTER(_Model)),
    ctypes.POINTER(_ModelDefinition)]
_dnnets_lib.dnnets_create.restype = ctypes.c_uint32

_dnnets_lib.dnnets_free_model_definition.argtypes = [
    ctypes.POINTER(_ModelDefinition)]
_dnnets_lib.dnnets_free_model_definition.restype = None

_dnnets_lib.dnnets_load.argtypes = [
    ctypes.POINTER(ctypes.POINTER(_Model)), ctypes.c_char_p]
_dnnets_lib.dnnets_load.restype = ctypes.c_uint32

_dnnets_lib.dnnets_forward_pass.argtypes = [
    ctypes.POINTER(_Model), ctypes.POINTER(ctypes.c_float),
    ctypes.c_uint32]
_dnnets_lib.dnnets_forward_pass.restype = None

_dnnets_lib.dnnets_get_output_buffer.argtypes = [ctypes.POINTER(_Model)]
_dnnets_lib.dnnets_get_output_buffer.restype = ctypes.POINTER(ctypes.c_float)

_dnnets_lib.dnnets_get_output_len.argtypes = [ctypes.POINTER(_Model)]
_dnnets_lib.dnnets_get_output_len.restype = ctypes.c_uint32

_dnnets_lib.dnnets_free_model.argtypes = [ctypes.POINTER(_Model)]
_dnnets_lib.dnnets_free_model.restype = None

_dnnets_lib.dnnets_print_layers.argtypes = [ctypes.POINTER(_Model)]
_dnnets_lib.dnnets_print_layers.restype = None


class Model:
    """
    A runtime model that can run a forward pass.

    Do not create objects of this class yourself.
    Use `load` or `ModelDefinition.create` instead.
    """

    def __init__(self, ptr) -> None:
        self._ptr = ptr

    def forward_pass_no_out(
        self, input: Union[Sequence[float], "np.typing.NDArray[np.float32]"]
    ) -> None:
        """
        Runs a forward pass and returns None.
        This is useful if you want to call `Model.out_buffer` at some later
        point.
        If you are only reading from the output buffer, a single call to
        `Model.out_buffer_ref` might be sufficient for all subsequent
        forward passes. The values behind the references will update with the
        next forward pass on this model.
        """

        if _use_numpy:
            input_len = input.size
            input_ptr = input.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        else:
            input_len = len(input)
            FloatArray = ctypes.c_float * input_len
            input_ptr = FloatArray(*input)
        _dnnets_lib.dnnets_forward_pass(self._ptr, input_ptr, input_len)

    def forward_pass(
        self, input: Union[Sequence[float], "np.typing.NDArray[np.float32]"]
    ) -> Union[List[float], "np.typing.NDArray[np.float32]"]:
        """
        Runs a forward pass and returns its output.
        """
        self.forward_pass_no_out(input)
        return self.out_buffer()

    def out_buffer_ref(
        self
    ) -> Union[List[float], "np.typing.NDArray[np.float32]"]:
        """
        Returns a reference to the output buffer of the model when using NumPy.
        Otherwise, it just returns a copy of the output of the last forward
        pass.

        Important: the reference to the output buffer is only valid as long as
        the model exists. As soon as the memory of the model is freed, the
        reference is no longer valid.
        """

        ptr = _dnnets_lib.dnnets_get_output_buffer(self._ptr)
        len = _dnnets_lib.dnnets_get_output_len(self._ptr)
        if _use_numpy:
            return np.ctypeslib.as_array(ptr, shape=(len,))
        else:
            return [ptr[i] for i in range(len)]

    def out_buffer(
        self
    ) -> Union[List[float], "np.typing.NDArray[np.float32]"]:
        """Returns the output of the last forward pass."""

        ptr = _dnnets_lib.dnnets_get_output_buffer(self._ptr)
        len = _dnnets_lib.dnnets_get_output_len(self._ptr)
        if _use_numpy:
            return np.ctypeslib.as_array(ptr, shape=(len,)).copy()
        else:
            return [ptr[i] for i in range(len)]

    def print_layers(self) -> None:
        """
        Prints each layer together with its configuration values to stderr.
        Weights and biases are excluded to keep the output readable.

        This function is indented for debugging use only.
        """

        _dnnets_lib.dnnets_print_layers(self._ptr)

    def _free(self) -> None:
        if self._ptr:
            _dnnets_lib.dnnets_free_model(self._ptr)
            self._ptr = None

    def __del__(self) -> None:
        self._free()


def load(path: str) -> Model:
    """Loads a model from a JSON file."""

    model_ptr = ctypes.POINTER(_Model)()
    result = _dnnets_lib.dnnets_load(ctypes.byref(model_ptr),
                                     path.encode("utf-8"))
    if result != _DnnetsResult.SUCCESS:
        raise RuntimeError(f"unable to load model: {
            _DnnetsResult(result).name}")
    return Model(model_ptr)


class ModelDefinition:
    """
    A model definition that can be used to create a `Model` programatically.
    """

    def __init__(self, input_layer_size: int) -> None:
        """
        Creates a new model definition.
        `input_layer_size` is the size of the input layer.
        """
        self._ptr = ctypes.POINTER(_ModelDefinition)()
        result = _dnnets_lib.dnnets_new_model_definition(
            ctypes.byref(self._ptr), input_layer_size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to create new model definition: {
                               _DnnetsResult(result).name}")
        self._mem_in_use = []

    def add_linear(
        self,
        size: int,
        weights: Union[
            Sequence[Sequence[float]], "np.typing.NDArray[np.float32]"
        ],
        biases: Union[Sequence[float], "np.typing.NDArray[np.float32]"]
    ) -> None:
        """Adds a new linear layer to the model definition."""

        linear = _Linear()
        if _use_numpy:
            weights_contiguous = np.ascontiguousarray(weights)
            weights_ptr = weights_contiguous.ctypes.data_as(
                ctypes.POINTER(ctypes.c_float))
            self._mem_in_use.append(weights_contiguous)
            biases_ptr = biases.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            self._mem_in_use.append(biases)
        else:
            weights_flat = [float(x) for neuron in weights for x in neuron]
            FloatArray = ctypes.c_float * len(weights_flat)
            weights_ptr = FloatArray(*weights_flat)
            self._mem_in_use.append(weights_ptr)
            FloatArray = ctypes.c_float * len(biases)
            biases_ptr = FloatArray(*biases)
            self._mem_in_use.append(biases_ptr)
        linear.weights = weights_ptr
        linear.biases = biases_ptr

        result = _dnnets_lib.dnnets_add_linear(self._ptr, linear, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add linear layer: {
                _DnnetsResult(result).name}")

    def add_layer_norm(
        self,
        size: int,
        weights: Union[Sequence[float], "np.typing.NDArray[np.float32]"],
        biases: Union[Sequence[float], "np.typing.NDArray[np.float32]"],
        eps: float = 1e-5
    ) -> None:
        """Adds a new layer normalization layer to the model definition."""

        layer_norm = _LayerNorm()
        if _use_numpy:
            weights_ptr = weights.ctypes.data_as(
                ctypes.POINTER(ctypes.c_float))
            self._mem_in_use.append(weights)
            biases_ptr = biases.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            self._mem_in_use.append(biases)
        else:
            FloatArray = ctypes.c_float * len(weights)
            weights_ptr = FloatArray(*weights)
            self._mem_in_use.append(weights_ptr)
            FloatArray = ctypes.c_float * len(biases)
            biases_ptr = FloatArray(*biases)
            self._mem_in_use.append(biases_ptr)
        layer_norm.weights = weights_ptr
        layer_norm.biases = biases_ptr
        layer_norm.eps = eps

        result = _dnnets_lib.dnnets_add_layer_norm(self._ptr, layer_norm, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add layer normalization layer: {
                _DnnetsResult(result).name}")

    def add_clip(self, size: int, min: float, max: float) -> None:
        """Adds a new clipping layer to the model definition."""

        clip = _Clip()
        clip.min = min
        clip.max = max
        result = _dnnets_lib.dnnets_add_clip(self._ptr, clip, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add clipping layer: {
                _DnnetsResult(result).name}")

    def add_elu(self, size: int, alpha: float = 1.0) -> None:
        """Adds a new ELU layer to the model definition."""

        elu = _ELU()
        elu.alpha = alpha
        result = _dnnets_lib.dnnets_add_elu(self._ptr, elu, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add ELU layer: {
                _DnnetsResult(result).name}")

    def add_relu(self, size: int) -> None:
        """Adds a new ReLU layer to the model definition."""

        result = _dnnets_lib.dnnets_add_relu(self._ptr, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add ReLU layer: {
                _DnnetsResult(result).name}")

    def add_relu6(self, size: int) -> None:
        """Adds a new ReLU6 layer to the model definition."""

        result = _dnnets_lib.dnnets_add_relu6(self._ptr, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add ReLU6 layer: {
                _DnnetsResult(result).name}")

    def add_sigmoid(self, size: int) -> None:
        """Adds a new sigmoid layer to the model definition."""

        result = _dnnets_lib.dnnets_add_sigmoid(self._ptr, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add sigmoid layer: {
                _DnnetsResult(result).name}")

    def add_tanh(self, size: int) -> None:
        """Adds a new tanh layer to the model definition."""

        result = _dnnets_lib.dnnets_add_tanh(self._ptr, size)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to add tanh layer: {
                _DnnetsResult(result).name}")

    def create(self) -> Model:
        """
        Creates a new `Model` from this definition.

        This method can be called multiple times for the same definition.
        This might be useful if it is desired to run the same model multiple
        times concurrently.
        """

        model_ptr = ctypes.POINTER(_Model)()
        result = _dnnets_lib.dnnets_create(ctypes.byref(model_ptr), self._ptr)
        if result != _DnnetsResult.SUCCESS:
            raise RuntimeError(f"unable to create model: {
                _DnnetsResult(result).name}")
        return Model(model_ptr)

    def _free(self) -> None:
        if self._ptr:
            _dnnets_lib.dnnets_free_model_definition(self._ptr)
            self._ptr = None

    def __del__(self) -> None:
        self._free()


def _init() -> None:
    _dnnets_lib.dnnets_init()


def _deinit() -> None:
    result = _dnnets_lib.dnnets_deinit()
    if result == _DnnetsResult.MEMORY_LEAK:
        warnings.warn(
            "Detected a memory leak in dnnets", category=RuntimeWarning)


# Initialize the library
_dnnets_lib.dnnets_init()
# Deinitialization is not really that important...
