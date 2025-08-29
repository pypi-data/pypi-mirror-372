from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AppException (SpireObject) :
    """
    Represents a standard internal exception type.
    
    This exception is raised for application-specific errors.
    """
