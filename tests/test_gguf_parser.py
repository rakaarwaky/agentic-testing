import os
import sys
import importlib.util

import pytest

gguf_path = "/home/raka/llama.cpp/llama-tui/src/infrastructure/gguf_parser.py"
if not os.path.exists(gguf_path):
    pytest.skip("gguf_parser not found — external dependency", allow_module_level=True)

spec = importlib.util.spec_from_file_location("gguf_parser", gguf_path)
if spec and spec.loader:
    module = importlib.util.module_from_spec(spec)
    sys.modules["gguf_parser"] = module
    spec.loader.exec_module(module)
from gguf_parser import *
