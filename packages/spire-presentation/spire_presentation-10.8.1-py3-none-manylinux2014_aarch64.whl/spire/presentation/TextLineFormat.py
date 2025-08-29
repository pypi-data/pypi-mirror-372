from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextLineFormat (  IActiveSlide, IChartGridLine) :
    """
    Represents the formatting properties for a line in a presentation.
    """
    @dispatch

    def Equals(self ,obj:SpireObject)->bool:
        """
        Determines if two LineFormat objects are equivalent.
        
        Args:
            obj: LineFormat object to compare with current instance
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextLineFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextLineFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_Equals,self.Ptr, intPtrobj)
        return ret

    @dispatch

    def Equals(self ,lf:'TextLineFormat')->bool:
        """
        Determines if two LineFormat instances are equivalent.
        
        Args:
            lf: LineFormat object to compare with current instance
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrlf:c_void_p = lf.Ptr

        GetDllLibPpt().TextLineFormat_EqualsL.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextLineFormat_EqualsL.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_EqualsL,self.Ptr, intPtrlf)
        return ret

    @property

    def FillFormat(self)->'LineFillFormat':
        """
        Gets the fill formatting properties of the line.
        
        Read-only access to complex fill definitions.
        """
        GetDllLibPpt().TextLineFormat_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormat_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else LineFillFormat(intPtr)
        return ret


    @property

    def FillType(self)->'FillFormatType':
        """
        Gets or sets the base type of fill formatting.
        
        Determines what kind of fill (solid, gradient, pattern, etc.) is applied.
        """
        GetDllLibPpt().TextLineFormat_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_FillType,self.Ptr)
        objwraped = FillFormatType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'FillFormatType'):
        GetDllLibPpt().TextLineFormat_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_FillType,self.Ptr, value.value)

    @property

    def Gradient(self)->'GradientFillFormat':
        """
        Gets the gradient fill formatting properties.
        
        Read-only access to gradient fill definitions.
        """
        GetDllLibPpt().TextLineFormat_get_Gradient.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormat_get_Gradient,self.Ptr)
        ret = None if intPtr==None else GradientFillFormat(intPtr)
        return ret


    @property

    def Pattern(self)->'PatternFillFormat':
        """
        Gets the pattern fill formatting properties.
        
        Read-only access to pattern fill definitions.
        """
        GetDllLibPpt().TextLineFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_Pattern.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormat_get_Pattern,self.Ptr)
        ret = None if intPtr==None else PatternFillFormat(intPtr)
        return ret


    @property

    def SolidFillColor(self)->'ColorFormat':
        """
        Gets the solid fill color properties.
        
        Read-only access to solid color fill definitions.
        """
        GetDllLibPpt().TextLineFormat_get_SolidFillColor.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_SolidFillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormat_get_SolidFillColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def RotateWithShape(self)->'TriState':
        """
        Determines if fill rotates with shape transformation.
        
        Read/write property controlling fill rotation behavior.
        """
        GetDllLibPpt().TextLineFormat_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_RotateWithShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_RotateWithShape,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RotateWithShape.setter
    def RotateWithShape(self, value:'TriState'):
        GetDllLibPpt().TextLineFormat_set_RotateWithShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_RotateWithShape,self.Ptr, value.value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the line.
        
        Read/write property controlling line thickness.
        """
        GetDllLibPpt().TextLineFormat_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().TextLineFormat_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_Width,self.Ptr, value)

    @property

    def DashStyle(self)->'LineDashStyleType':
        """
        Gets or sets the dash pattern of the line.
        
        Read/write property controlling line dash appearance.
        """
        GetDllLibPpt().TextLineFormat_get_DashStyle.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_DashStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_DashStyle,self.Ptr)
        objwraped = LineDashStyleType(ret)
        return objwraped

    @DashStyle.setter
    def DashStyle(self, value:'LineDashStyleType'):
        GetDllLibPpt().TextLineFormat_set_DashStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_DashStyle,self.Ptr, value.value)

    @property

    def CapStyle(self)->'LineCapStyle':
        """
        Gets or sets the line end cap style.
        
        Read/write property controlling line end appearance.
        """
        GetDllLibPpt().TextLineFormat_get_CapStyle.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_CapStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_CapStyle,self.Ptr)
        objwraped = LineCapStyle(ret)
        return objwraped

    @CapStyle.setter
    def CapStyle(self, value:'LineCapStyle'):
        GetDllLibPpt().TextLineFormat_set_CapStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_CapStyle,self.Ptr, value.value)

    @property

    def Style(self)->'TextLineStyle':
        """
        Gets or sets the overall line style.
        
        Read/write property controlling line appearance.
        """
        GetDllLibPpt().TextLineFormat_get_Style.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_Style,self.Ptr)
        objwraped = TextLineStyle(ret)
        return objwraped

    @Style.setter
    def Style(self, value:'TextLineStyle'):
        GetDllLibPpt().TextLineFormat_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_Style,self.Ptr, value.value)

    @property

    def Alignment(self)->'PenAlignmentType':
        """
        Gets or sets the line alignment.
        
        Read/write property controlling line positioning.
        """
        GetDllLibPpt().TextLineFormat_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_Alignment,self.Ptr)
        objwraped = PenAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'PenAlignmentType'):
        GetDllLibPpt().TextLineFormat_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_Alignment,self.Ptr, value.value)

    @property

    def JoinStyle(self)->'LineJoinType':
        """
        Gets or sets the line join style.
        
        Read/write property controlling corner appearance.
        """
        GetDllLibPpt().TextLineFormat_get_JoinStyle.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_JoinStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_JoinStyle,self.Ptr)
        objwraped = LineJoinType(ret)
        return objwraped

    @JoinStyle.setter
    def JoinStyle(self, value:'LineJoinType'):
        GetDllLibPpt().TextLineFormat_set_JoinStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_JoinStyle,self.Ptr, value.value)

    @property
    def MiterLimit(self)->float:
        """
        Gets or sets the miter limit for corners.
        
        Read/write property controlling angle sharpness.
        """
        GetDllLibPpt().TextLineFormat_get_MiterLimit.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_MiterLimit.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_MiterLimit,self.Ptr)
        return ret

    @MiterLimit.setter
    def MiterLimit(self, value:float):
        GetDllLibPpt().TextLineFormat_set_MiterLimit.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_MiterLimit,self.Ptr, value)

    @property

    def LineBeginType(self)->'LineEndType':
        """
        Gets or sets the arrowhead style at line start.
        
        Read/write property controlling start decoration.
        """
        GetDllLibPpt().TextLineFormat_get_LineBeginType.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_LineBeginType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_LineBeginType,self.Ptr)
        objwraped = LineEndType(ret)
        return objwraped

    @LineBeginType.setter
    def LineBeginType(self, value:'LineEndType'):
        GetDllLibPpt().TextLineFormat_set_LineBeginType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_LineBeginType,self.Ptr, value.value)

    @property

    def LineEndType(self)->'LineEndType':
        """
        Gets or sets the arrowhead style at line end.
        
        Read/write property controlling end decoration.
        """
        GetDllLibPpt().TextLineFormat_get_LineEndType.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_LineEndType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_LineEndType,self.Ptr)
        objwraped = LineEndType(ret)
        return objwraped

    @LineEndType.setter
    def LineEndType(self, value:'LineEndType'):
        GetDllLibPpt().TextLineFormat_set_LineEndType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_LineEndType,self.Ptr, value.value)

    @property

    def LineBeginWidth(self)->'LineEndWidth':
        """
        Gets or sets the arrowhead width at line start.
        
        Read/write property controlling start decoration size.
        """
        GetDllLibPpt().TextLineFormat_get_LineBeginWidth.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_LineBeginWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_LineBeginWidth,self.Ptr)
        objwraped = LineEndWidth(ret)
        return objwraped

    @LineBeginWidth.setter
    def LineBeginWidth(self, value:'LineEndWidth'):
        GetDllLibPpt().TextLineFormat_set_LineBeginWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_LineBeginWidth,self.Ptr, value.value)

    @property

    def LineEndWidth(self)->'LineEndWidth':
        """
        Gets or sets the arrowhead width at line end.
        
        Read/write property controlling end decoration size.
        """
        GetDllLibPpt().TextLineFormat_get_LineEndWidth.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_LineEndWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_LineEndWidth,self.Ptr)
        objwraped = LineEndWidth(ret)
        return objwraped

    @LineEndWidth.setter
    def LineEndWidth(self, value:'LineEndWidth'):
        GetDllLibPpt().TextLineFormat_set_LineEndWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_LineEndWidth,self.Ptr, value.value)

    @property

    def LineBeginLength(self)->'LineEndLength':
        """
        Gets or sets the arrowhead length at line start.
        
        Read/write property controlling start decoration size.
        """
        GetDllLibPpt().TextLineFormat_get_LineBeginLength.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_LineBeginLength.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_LineBeginLength,self.Ptr)
        objwraped = LineEndLength(ret)
        return objwraped

    @LineBeginLength.setter
    def LineBeginLength(self, value:'LineEndLength'):
        GetDllLibPpt().TextLineFormat_set_LineBeginLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_LineBeginLength,self.Ptr, value.value)

    @property

    def LineEndLength(self)->'LineEndLength':
        """
        Gets or sets the arrowhead length at line end.
        
        Read/write property controlling end decoration size.
        """
        GetDllLibPpt().TextLineFormat_get_LineEndLength.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_get_LineEndLength.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_get_LineEndLength,self.Ptr)
        objwraped = LineEndLength(ret)
        return objwraped

    @LineEndLength.setter
    def LineEndLength(self, value:'LineEndLength'):
        GetDllLibPpt().TextLineFormat_set_LineEndLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextLineFormat_set_LineEndLength,self.Ptr, value.value)

    def GetHashCode(self)->int:
        """
        Generates a hash code for the LineFormat object.
        
        Returns:
            int: Hash code representing object state
        """
        GetDllLibPpt().TextLineFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormat_GetHashCode,self.Ptr)
        return ret

