import os
import sys

generated_files_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(generated_files_path)

# Remove legacy paths
path_to_remove1 = "/home/user/dev/runtest/Release/IndyDeployment/PythonMiddleware/interfaces/impl"
path_to_remove2 = "/home/user/release/IndyDeployment/PythonMiddleware/interfaces/impl"
if path_to_remove1 in sys.path: sys.path.remove(path_to_remove1)
if path_to_remove2 in sys.path: sys.path.remove(path_to_remove2)

# gRPC service stubs
from .boot_pb2_grpc         import *
from .config_pb2_grpc       import *
from .control_pb2_grpc      import *
from .cri_pb2_grpc          import *
from .device_pb2_grpc       import *
from .ethercat_pb2_grpc     import *
from .linear_pb2_grpc       import *
from .moby_pb2_grpc         import *
from .rtde_pb2_grpc         import *
from .teleop_dev_pb2_grpc   import *

# Protocol message types
from . import boot_msgs_pb2     as boot_msgs
from . import common_msgs_pb2   as common_msgs
from . import config_msgs_pb2   as config_msgs
from . import control_msgs_pb2  as control_msgs
from . import cri_msgs_pb2      as cri_msgs
from . import device_msgs_pb2   as device_msgs
from . import ethercat_msgs_pb2 as ethercat_msgs
from . import moby_msgs_pb2     as moby_msgs
from . import rtde_msgs_pb2     as rtde_msgs
from . import teleop_dev_pb2    as teleop_data
