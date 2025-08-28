import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from .indydcp3 import IndyDCP3
from .indydcp2 import IndyDCP2
from .eye import IndyEye
from .ecat import EtherCAT
from .moby import MobyClient
# from .motor import MotorClient

from .enums import *
__all__ = ['IndyDCP3', 'StopCategory', 'JointBaseType', 'TaskBaseType']
