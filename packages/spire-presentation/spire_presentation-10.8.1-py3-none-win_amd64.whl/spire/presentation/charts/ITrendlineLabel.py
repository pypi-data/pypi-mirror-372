from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITrendlineLabel (SpireObject) :
    """
    Represents the label properties for a trendline in a chart.
    
    This interface provides access to formatting and positioning properties 
    for trendline labels, including text properties and offset coordinates.
    """
    @property
    def TextFrameProperties(self)->'ITextFrameProperties':
        """
        Gets the text formatting properties for the trendline label.
        
        Returns:
            ITextFrameProperties: An object containing text formatting settings 
            such as paragraphs, margins, and text styles.
        """
        GetDllLibPpt().ITrendlineLabel_get_TextFrameProperties.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlineLabel_get_TextFrameProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlineLabel_get_TextFrameProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property
    def OffsetX(self)->float:
        """
        Gets or sets the horizontal offset of the trendline label.
        
        The offset is relative to the default position as a percentage of the chart width.
        Positive values move the label right, negative values move it left.
        
        Returns:
            float: Current horizontal offset value.
        """
        GetDllLibPpt().ITrendlineLabel_get_OffsetX.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlineLabel_get_OffsetX.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlineLabel_get_OffsetX,self.Ptr)
        return ret

    @OffsetX.setter
    def OffsetX(self, value:float):
        GetDllLibPpt().ITrendlineLabel_set_OffsetX.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlineLabel_set_OffsetX,self.Ptr, value)

    @property
    def OffsetY(self)->float:
        """
        Gets or sets the vertical offset of the trendline label.
        
        The offset is relative to the default position as a percentage of the chart height.
        Positive values move the label down, negative values move it up.
        
        Returns:
            float: Current vertical offset value.
        """
        GetDllLibPpt().ITrendlineLabel_get_OffsetY.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlineLabel_get_OffsetY.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlineLabel_get_OffsetY,self.Ptr)
        return ret

    @OffsetY.setter
    def OffsetY(self, value:float):
        GetDllLibPpt().ITrendlineLabel_set_OffsetY.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlineLabel_set_OffsetY,self.Ptr, value)

