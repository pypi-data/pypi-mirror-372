import onnx
import json
import warnings
from pathlib import Path
from typing import Any, IO, Text, Union


def load_model(
        f: Union[IO, Text],
        format: Any = None,
        load_external_data: bool = True,
) -> onnx.ModelProto:
    """Load model from ONNX file.

    This is a wrapper to `onnx.load_model` that automatically falls back to
    `load_external_data=False` when tensors are stripped.

    Args:
        f: A file-like object or a string file path to be written to this
            file.
        format: A reserved arg
        load_external_data: If True and the external data under the same
            directory of the model, load the external data
    """
    try:
        return onnx.load_model(f, format=format, load_external_data=load_external_data)
    except (OSError, onnx.checker.ValidationError) as e:  # The ONNX may contain stripped large tensors.
        if (load_external_data
                and isinstance(e, OSError)
                and json.loads(Path(e.filename).name)["type"] != "stripped"):
            raise
        warnings.warn(
            'The specified ONNX contains stripped large tensors. '
            'Falling back to `load_external_data=False`.',
            UserWarning)
        return onnx.load_model(f, format=format, load_external_data=False)
