from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IChartGridLine (SpireObject) :
    """
    Represents the gridlines on a chart axis in a presentation.

    This class provides properties to format the appearance of chart gridlines,
    including line style, width, color, dash style, arrowheads, and fill formatting.
    """
    @property

    def FillType(self)->'FillFormatType':
        """
        Gets or sets the fill format type.
    
        """
        GetDllLibPpt().IChartGridLine_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_FillType,self.Ptr)
        objwraped = FillFormatType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'FillFormatType'):
        GetDllLibPpt().IChartGridLine_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_FillType,self.Ptr, value.value)

    @property

    def FillFormat(self)->'LineFillFormat':
        """
        Gets the fill format of a line..
    
        """
        GetDllLibPpt().IChartGridLine_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartGridLine_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else LineFillFormat(intPtr)
        return ret


    @property

    def Gradient(self)->'GradientFillFormat':
        """
        Gets the Gradient fill format.
    
        """
        GetDllLibPpt().IChartGridLine_get_Gradient.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartGridLine_get_Gradient,self.Ptr)
        ret = None if intPtr==None else GradientFillFormat(intPtr)
        return ret


    @property

    def Pattern(self)->'PatternFillFormat':
        """
        Gets the pattern fill format.
    
        """
        GetDllLibPpt().IChartGridLine_get_Pattern.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_Pattern.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartGridLine_get_Pattern,self.Ptr)
        ret = None if intPtr==None else PatternFillFormat(intPtr)
        return ret


    @property

    def SolidFillColor(self)->'ColorFormat':
        """
        Gets the color of a solid fill.
    
        """
        GetDllLibPpt().IChartGridLine_get_SolidFillColor.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_SolidFillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartGridLine_get_SolidFillColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def RotateWithShape(self)->'TriState':
        """
        Indicates whether the fill should be rotated with a shape.
    
        """
        GetDllLibPpt().IChartGridLine_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_RotateWithShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_RotateWithShape,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RotateWithShape.setter
    def RotateWithShape(self, value:'TriState'):
        GetDllLibPpt().IChartGridLine_set_RotateWithShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_RotateWithShape,self.Ptr, value.value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of a line.
    
        """
        GetDllLibPpt().IChartGridLine_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IChartGridLine_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_Width,self.Ptr, value)

    @property

    def DashStyle(self)->'LineDashStyleType':
        """
        Gets or sets the line dash style.
    
        """
        GetDllLibPpt().IChartGridLine_get_DashStyle.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_DashStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_DashStyle,self.Ptr)
        objwraped = LineDashStyleType(ret)
        return objwraped

    @DashStyle.setter
    def DashStyle(self, value:'LineDashStyleType'):
        GetDllLibPpt().IChartGridLine_set_DashStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_DashStyle,self.Ptr, value.value)

    @property

    def CapStyle(self)->'LineCapStyle':
        """
        Gets or sets the line cap style.
           
        """
        GetDllLibPpt().IChartGridLine_get_CapStyle.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_CapStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_CapStyle,self.Ptr)
        objwraped = LineCapStyle(ret)
        return objwraped

    @CapStyle.setter
    def CapStyle(self, value:'LineCapStyle'):
        GetDllLibPpt().IChartGridLine_set_CapStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_CapStyle,self.Ptr, value.value)

    @property

    def Style(self)->'TextLineStyle':
        """
        Gets or sets the line style.
           
        """
        GetDllLibPpt().IChartGridLine_get_Style.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_Style,self.Ptr)
        objwraped = TextLineStyle(ret)
        return objwraped

    @Style.setter
    def Style(self, value:'TextLineStyle'):
        GetDllLibPpt().IChartGridLine_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_Style,self.Ptr, value.value)

    @property

    def Alignment(self)->'PenAlignmentType':
        """
        Gets or sets the line alignment.
            
        """
        GetDllLibPpt().IChartGridLine_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_Alignment,self.Ptr)
        objwraped = PenAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'PenAlignmentType'):
        GetDllLibPpt().IChartGridLine_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_Alignment,self.Ptr, value.value)

    @property

    def JoinStyle(self)->'LineJoinType':
        """
        Gets or sets the lines join style.
           
        """
        GetDllLibPpt().IChartGridLine_get_JoinStyle.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_JoinStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_JoinStyle,self.Ptr)
        objwraped = LineJoinType(ret)
        return objwraped

    @JoinStyle.setter
    def JoinStyle(self, value:'LineJoinType'):
        GetDllLibPpt().IChartGridLine_set_JoinStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_JoinStyle,self.Ptr, value.value)

    @property
    def MiterLimit(self)->float:
        """
        Gets or sets the miter limit of a line.
            
        """
        GetDllLibPpt().IChartGridLine_get_MiterLimit.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_MiterLimit.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_MiterLimit,self.Ptr)
        return ret

    @MiterLimit.setter
    def MiterLimit(self, value:float):
        GetDllLibPpt().IChartGridLine_set_MiterLimit.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_MiterLimit,self.Ptr, value)

    @property

    def LineBeginType(self)->'LineEndType':
        """
        Gets or sets the arrowhead style at the beginning of a line.
            
        """
        GetDllLibPpt().IChartGridLine_get_LineBeginType.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_LineBeginType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_LineBeginType,self.Ptr)
        objwraped = LineEndType(ret)
        return objwraped

    @LineBeginType.setter
    def LineBeginType(self, value:'LineEndType'):
        GetDllLibPpt().IChartGridLine_set_LineBeginType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_LineBeginType,self.Ptr, value.value)

    @property

    def LineEndType(self)->'LineEndType':
        """
        Gets or sets the arrowhead style at the end of a line.
           
        """
        GetDllLibPpt().IChartGridLine_get_LineEndType.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_LineEndType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_LineEndType,self.Ptr)
        objwraped = LineEndType(ret)
        return objwraped

    @LineEndType.setter
    def LineEndType(self, value:'LineEndType'):
        GetDllLibPpt().IChartGridLine_set_LineEndType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_LineEndType,self.Ptr, value.value)

    @property

    def LineBeginWidth(self)->'LineEndWidth':
        """
        Gets or sets the arrowhead width at the beginning of a line.
          
        """
        GetDllLibPpt().IChartGridLine_get_LineBeginWidth.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_LineBeginWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_LineBeginWidth,self.Ptr)
        objwraped = LineEndWidth(ret)
        return objwraped

    @LineBeginWidth.setter
    def LineBeginWidth(self, value:'LineEndWidth'):
        GetDllLibPpt().IChartGridLine_set_LineBeginWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_LineBeginWidth,self.Ptr, value.value)

    @property

    def LineEndWidth(self)->'LineEndWidth':
        """
        Gets or sets the arrowhead width at the end of a line.
            
        """
        GetDllLibPpt().IChartGridLine_get_LineEndWidth.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_LineEndWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_LineEndWidth,self.Ptr)
        objwraped = LineEndWidth(ret)
        return objwraped

    @LineEndWidth.setter
    def LineEndWidth(self, value:'LineEndWidth'):
        GetDllLibPpt().IChartGridLine_set_LineEndWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_LineEndWidth,self.Ptr, value.value)

    @property

    def LineBeginLength(self)->'LineEndLength':
        """
        Gets or sets the arrowhead length at the beginning of a line.
           
        """
        GetDllLibPpt().IChartGridLine_get_LineBeginLength.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_LineBeginLength.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_LineBeginLength,self.Ptr)
        objwraped = LineEndLength(ret)
        return objwraped

    @LineBeginLength.setter
    def LineBeginLength(self, value:'LineEndLength'):
        GetDllLibPpt().IChartGridLine_set_LineBeginLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_LineBeginLength,self.Ptr, value.value)

    @property

    def LineEndLength(self)->'LineEndLength':
        """
        Gets or sets the arrowhead length at the end of a line.
           
        """
        GetDllLibPpt().IChartGridLine_get_LineEndLength.argtypes=[c_void_p]
        GetDllLibPpt().IChartGridLine_get_LineEndLength.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChartGridLine_get_LineEndLength,self.Ptr)
        objwraped = LineEndLength(ret)
        return objwraped

    @LineEndLength.setter
    def LineEndLength(self, value:'LineEndLength'):
        GetDllLibPpt().IChartGridLine_set_LineEndLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChartGridLine_set_LineEndLength,self.Ptr, value.value)

