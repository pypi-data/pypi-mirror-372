from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LegendEntry (SpireObject) :
    """
    Represents an entry in a chart legend.

    Contains formatting and text properties for individual legend items.
    """
    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
        Gets text formatting properties.

        Returns:
            ITextFrameProperties: Text formatting settings.
        """
        GetDllLibPpt().LegendEntry_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().LegendEntry_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LegendEntry_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


