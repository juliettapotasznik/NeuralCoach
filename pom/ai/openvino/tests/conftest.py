import sys
import os
from pathlib import Path

# Add ai/openvino to sys.path so we can import modules
openvino_path = Path(__file__).parent.parent
sys.path.append(str(openvino_path))
