from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class HistogramAxisFormat (SpireObject) :
    """
    Class provide the options for Histogram and Pareto Chart axis
    
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Check for the equals an object
   
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().HistogramAxisFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().HistogramAxisFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().HistogramAxisFormat_Equals,self.Ptr, intPtrobj)
        return ret

