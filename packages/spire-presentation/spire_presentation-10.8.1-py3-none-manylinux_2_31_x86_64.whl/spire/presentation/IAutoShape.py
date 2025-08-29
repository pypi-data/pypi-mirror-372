from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class IAutoShape (IShape) :
    """Represents an AutoShape in a presentation slide."""

    @property
    def Locking(self)->'ShapeLocking':
        """
        Gets shape's locks.
        
        Returns:
            ShapeLocking: Read-only shape locking settings.
        """
        GetDllLibPpt().IAutoShape_get_Locking.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Locking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Locking,self.Ptr)
        ret = None if intPtr==None else ShapeLocking(intPtr)
        return ret


    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
        Gets TextFrame object for the AutoShape.
        
        Returns:
            ITextFrameProperties: Read-only text frame properties.
        """
        GetDllLibPpt().IAutoShape_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property
    def UseBackgroundFill(self)->bool:
        """
        Indicates whether this autoshape should be filled with slide's background fill.
        
        Returns:
            bool: True if using background fill, False otherwise.
        """
        GetDllLibPpt().IAutoShape_get_UseBackgroundFill.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_UseBackgroundFill.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_UseBackgroundFill,self.Ptr)
        return ret

    @UseBackgroundFill.setter
    def UseBackgroundFill(self, value:bool):
        """
        Sets whether to use slide's background fill.
        
        Args:
            value (bool): True to use background fill, False otherwise.
        """
        GetDllLibPpt().IAutoShape_set_UseBackgroundFill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAutoShape_set_UseBackgroundFill,self.Ptr, value)

    @property

    def ShapeStyle(self)->'ShapeStyle':
        """Gets the shape style object."""
        GetDllLibPpt().IAutoShape_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """Gets the type of the shape."""
        GetDllLibPpt().IAutoShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        """
        Sets the type of the shape.
        
        Args:
            value (ShapeType): New shape type.
        """
        GetDllLibPpt().IAutoShape_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAutoShape_set_ShapeType,self.Ptr, value.value)

    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """Gets shape adjustment values collection."""
        GetDllLibPpt().IAutoShape_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is Placeholder.
        
        Returns:
            bool: True if placeholder, False otherwise.
        """
        GetDllLibPpt().IAutoShape_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_IsPlaceholder,self.Ptr)
        return ret

    @property
    def IsTextBox(self)->bool:
        """
        Indicates whether the shape is TextBox.
        
        Returns:
            bool: True if text box, False otherwise.
        """
        GetDllLibPpt().IAutoShape_get_IsTextBox.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_IsTextBox.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_IsTextBox,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets the placeholder for a shape.
        
        Returns:
            Placeholder: Read-only placeholder object.
        """
        GetDllLibPpt().IAutoShape_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the shape's tags collection.
        
        Returns:
            TagCollection: Read-only tag collection.
        """
        GetDllLibPpt().IAutoShape_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets the shape frame's properties.
        
        Returns:
            GraphicFrame: Frame properties object.
        """
        GetDllLibPpt().IAutoShape_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        """
        Sets the shape frame's properties.
        
        Args:
            value (GraphicFrame): New frame properties.
        """
        GetDllLibPpt().IAutoShape_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets line formatting properties.
        
        Returns:
            TextLineFormat: Read-only line format object.
        """
        GetDllLibPpt().IAutoShape_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets 3D effect properties.
        
        Returns:
            FormatThreeD: Read-only 3D format object.
        """
        GetDllLibPpt().IAutoShape_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets pixel effects applied to a shape.
        
        Returns:
            EffectDag: Read-only effect object (may be null).
        """
        GetDllLibPpt().IAutoShape_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill formatting properties.
        
        Returns:
            FillFormat: Read-only fill format object.
        """
        GetDllLibPpt().IAutoShape_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse click.
        
        Returns:
            ClickHyperlink: Hyperlink for click action.
        """
        GetDllLibPpt().IAutoShape_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        """
        Sets the hyperlink for mouse click.
        
        Args:
            value (ClickHyperlink): New click hyperlink.
        """
        GetDllLibPpt().IAutoShape_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse over.
        
        Returns:
            ClickHyperlink: Hyperlink for mouseover action.
        """
        GetDllLibPpt().IAutoShape_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        """
        Sets the hyperlink for mouse over.
        
        Args:
            value (ClickHyperlink): New mouseover hyperlink.
        """
        GetDllLibPpt().IAutoShape_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates whether the shape is hidden.
        
        Returns:
            bool: True if hidden, False otherwise.
        """
        GetDllLibPpt().IAutoShape_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        """
        Sets whether the shape is hidden.
        
        Args:
            value (bool): True to hide, False to show.
        """
        GetDllLibPpt().IAutoShape_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAutoShape_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
        
        Returns:
            ActiveSlide: Read-only parent slide.
        """
        GetDllLibPpt().IAutoShape_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets the position in z-order.
        
        Returns:
            int: Z-order position index.
        """
        GetDllLibPpt().IAutoShape_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        """
        Sets z-order position.
        
        Args:
            value (int): New z-order position.
        """
        GetDllLibPpt().IAutoShape_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAutoShape_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets rotation in degrees.
        
        Returns:
            float: Rotation angle in degrees.
        """
        GetDllLibPpt().IAutoShape_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        """
        Sets rotation angle.
        
        Args:
            value (float): New rotation in degrees.
        """
        GetDllLibPpt().IAutoShape_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets x-coordinate of upper-left corner.
        
        Returns:
            float: X-coordinate position.
        """
        GetDllLibPpt().IAutoShape_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        """
        Sets horizontal position.
        
        Args:
            value (float): New left position.
        """
        GetDllLibPpt().IAutoShape_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets y-coordinate of upper-left corner.
        
        Returns:
            float: Y-coordinate position.
        """
        GetDllLibPpt().IAutoShape_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        """
        Sets vertical position.
        
        Args:
            value (float): New top position.
        """
        GetDllLibPpt().IAutoShape_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets shape width.
        
        Returns:
            float: Width of the shape.
        """
        GetDllLibPpt().IAutoShape_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IAutoShape_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets shape height.
        
        Returns:
            float: Height of the shape.
        """
        GetDllLibPpt().IAutoShape_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        """
        Sets shape height.
        
        Args:
            value (float): New height value.
        """
        GetDllLibPpt().IAutoShape_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets alternative text.
        
        Returns:
            str: Alternative text string.
        """
        GetDllLibPpt().IAutoShape_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAutoShape_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        """
        Sets alternative text.
        
        Args:
            value (str): New alternative text.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAutoShape_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets shape name.
        
        Returns:
            str: Name of the shape.
        """
        GetDllLibPpt().IAutoShape_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAutoShape_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets shape name.
        
        Args:
            value (str): New shape name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAutoShape_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide.
        
        Returns:
            ActiveSlide: Read-only parent slide.
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IAutoShape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """Gets parent presentation object."""
        from spire.presentation import Presentation
        GetDllLibPpt().IAutoShape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property
    def ContainMathEquation(self)->bool:
        """
        Checks if shape contains math equation.
        
        Returns:
            bool: True if contains equation, False otherwise.
        """
        GetDllLibPpt().IAutoShape_get_ContainMathEquation.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ContainMathEquation.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_ContainMathEquation,self.Ptr)
        return ret


    def AppendTextFrame(self ,text:str):
        """
        Adds a new TextFrame or sets existing text.
        
        Args:
            text (str): Text content for the text frame.
        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().IAutoShape_AppendTextFrame.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IAutoShape_AppendTextFrame,self.Ptr,textPtr)

    def RemovePlaceholder(self):
        """Removes placeholder from the shape."""
        GetDllLibPpt().IAutoShape_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """Releases resources associated with the object."""
        GetDllLibPpt().IAutoShape_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_Dispose,self.Ptr)

    @property
    def Points(self)->List['PointF']:
        """
        Gets shape points.
        
        Returns:
            List[PointF]: Collection of shape points.
        """
        GetDllLibPpt().IAutoShape_get_Points.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Points.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().IAutoShape_get_Points,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PointF)
        return ret

