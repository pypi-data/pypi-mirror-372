import json
import pathlib

__all__ = (
    '__author__',
    '__contact__',
    '__homepage__',
    '__version__',
)


def _get_meta():
    f = pathlib.Path(__file__).parent / "_metadata.json"
    return json.loads(f.read_text())


_meta = _get_meta()
__author__ = _meta["author"]
__contact__ = __author__
__homepage__ = _meta["url"]
__version__ = _meta["version"]
del _meta
