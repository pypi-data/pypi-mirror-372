from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IShape (SpireObject) :
    """
    Represents a shape object in a presentation slide.
    Provides properties and methods for manipulating shape appearance, position, and content.
    Inherits from SpireObject.
    """
    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is a placeholder.
        Returns:
            bool: True if placeholder, False otherwise.
        """
        GetDllLibPpt().IShape_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IShape_get_IsPlaceholder,self.Ptr)
        return ret

    @property
    def IsTextBox(self)->bool:
        """
        Indicates whether the shape is a text box.
        Returns:
            bool: True if text box, False otherwise.
        """
        GetDllLibPpt().IShape_get_IsTextBox.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_IsTextBox.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IShape_get_IsTextBox,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets the placeholder properties of the shape (read-only).
        Returns:
            Placeholder: Placeholder object or None.
        """
        
        GetDllLibPpt().IShape_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the collection of tags associated with the shape.
        Returns:
            TagCollection: Collection of shape tags.
        """
        GetDllLibPpt().IShape_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets the graphic frame properties of the shape.
        Returns:
            GraphicFrame: Current graphic frame settings.
        """
        GetDllLibPpt().IShape_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        """
        Sets the graphic frame properties of the shape.
        Parameters:
            value: New GraphicFrame settings.
        """
        GetDllLibPpt().IShape_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IShape_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets line formatting properties.
        
        Returns:
            TextLineFormat: Line format object (may be null).
        """
        GetDllLibPpt().IShape_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets 3D effect properties.
        
        Returns:
            FormatThreeD: 3D format object (may be null).
        """
        GetDllLibPpt().IShape_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """""
        Gets effect properties.
        
        Returns:
            EffectDag: Effect object (may be null).
        """
        GetDllLibPpt().IShape_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill properties.
        
        Returns:
            FillFormat: Fill format object (may be null).
        """
        GetDllLibPpt().IShape_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets mouse click hyperlink.
        
        Returns:
            ClickHyperlink: Hyperlink for click action.
        """
        GetDllLibPpt().IShape_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        """
        Sets mouse click hyperlink.
        
        Args:
            value (ClickHyperlink): New click hyperlink.
        """
        GetDllLibPpt().IShape_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IShape_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets mouse over hyperlink.
        
        Returns:
            ClickHyperlink: Hyperlink for mouseover action.
        """
        GetDllLibPpt().IShape_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        """
        Sets mouse over hyperlink.
        
        Args:
            value (ClickHyperlink): New mouseover hyperlink.
        """
        GetDllLibPpt().IShape_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IShape_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates whether the shape is hidden.
        
        Returns:
            bool: True if hidden, False otherwise.
        """
        GetDllLibPpt().IShape_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IShape_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        """
        Sets shape visibility.
        
        Args:
            value (bool): True to hide, False to show.
        """
        GetDllLibPpt().IShape_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IShape_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
           
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IShape_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets z-order position.
        
        Returns:
            int: Position in z-order stack.
        """
        GetDllLibPpt().IShape_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IShape_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        """
        Sets z-order position.
        
        Args:
            value (int): New z-order position.
        """
        GetDllLibPpt().IShape_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IShape_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets rotation angle.
        
        Returns:
            float: Rotation in degrees (positive = clockwise).
        """
        GetDllLibPpt().IShape_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        """
        Sets rotation angle.
        
        Args:
            value (float): New rotation in degrees.
        """
        GetDllLibPpt().IShape_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets horizontal position.
        
        Returns:
            float: X-coordinate of upper-left corner.
        """
        GetDllLibPpt().IShape_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        """
        Sets horizontal position.
        
        Args:
            value (float): New left position.
        """
        GetDllLibPpt().IShape_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets vertical position.
        
        Returns:
            float: Y-coordinate of upper-left corner.
        """
        GetDllLibPpt().IShape_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        """
        Sets vertical position.
        
        Args:
            value (float): New top position.
        """
        GetDllLibPpt().IShape_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets object width.
        
        Returns:
            float: Width of the OLE object.
        """
        GetDllLibPpt().IShape_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        """
        Sets object width.
        
        Args:
            value (float): New width value.
        """
        GetDllLibPpt().IShape_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets object height.
        
        Returns:
            float: Height of the OLE object.
        """
        GetDllLibPpt().IShape_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        """
        Sets object height.
        
        Args:
            value (float): New height value.
        """
        GetDllLibPpt().IShape_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets alternative text.
        
        Returns:
            str: Alternative text description.
        """
        GetDllLibPpt().IShape_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IShape_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        """
        Sets alternative text.
        
        Args:
            value (str): New alternative text.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IShape_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IShape_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def AlternativeTitle(self)->str:
        """
        Gets or sets the alternative title associated with a shape.
           
        """
        GetDllLibPpt().IShape_get_AlternativeTitle.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_AlternativeTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IShape_get_AlternativeTitle,self.Ptr))
        return ret


    @AlternativeTitle.setter
    def AlternativeTitle(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IShape_set_AlternativeTitle.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IShape_set_AlternativeTitle,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets shape name.
        
        Returns:
            str: Name of the shape.
        """
        GetDllLibPpt().IShape_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IShape_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets shape name.
        
        Args:
            value (str): New shape name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IShape_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IShape_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets parent slide.
        
        Returns:
            ActiveSlide: Read-only parent slide.
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IShape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """Gets parent presentation."""
        from spire.presentation import Presentation
        GetDllLibPpt().IShape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    def RemovePlaceholder(self):
        """Removes placeholder properties from the shape."""
        GetDllLibPpt().IShape_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IShape_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
        Dispose object and free resources.
    
        """
        GetDllLibPpt().IShape_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IShape_Dispose,self.Ptr)


    def SetShapeAlignment(self ,shapeAlignment:'ShapeAlignment'):
        """
        Sets the alignment with a shape.
    
        """
        enumshapeAlignment:c_int = shapeAlignment.value

        GetDllLibPpt().IShape_SetShapeAlignment.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_SetShapeAlignment,self.Ptr, enumshapeAlignment)


    def SetShapeArrange(self ,shapeArrange:'ShapeArrange'):
        """
        Sets the arrangement with a shape.
    
        """
        enumshapeArrange:c_int = shapeArrange.value

        GetDllLibPpt().IShape_SetShapeArrange.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_SetShapeArrange,self.Ptr, enumshapeArrange)


    def InsertVideo(self ,filepath:str):
        """
        Insert a video into placeholder shape.
        Args:
            filepath:Video file path.
        """
        
        filepathPtr = StrToPtr(filepath)
        GetDllLibPpt().IShape_InsertVideo.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IShape_InsertVideo,self.Ptr,filepathPtr)


    def InsertSmartArt(self ,smartArtLayoutType:'SmartArtLayoutType'):
        """
        Insert a smartArt into placeholder shape.
        Args:
            type:smartArt Type.
        """
        enumsmartArtLayoutType:c_int = smartArtLayoutType.value

        GetDllLibPpt().IShape_InsertSmartArt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_InsertSmartArt,self.Ptr, enumsmartArtLayoutType)


    def InsertChart(self ,type:'ChartType'):
        """
        Insert a chart into placeholder shape.
        Args:
            type:Chart Type.
        """
        enumtype:c_int = type.value

        GetDllLibPpt().IShape_InsertChart.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_InsertChart,self.Ptr, enumtype)


    def InsertTable(self ,tableColumnCount:int,tableRowCount:int):
        """
        Insert a table into placeholder shape.
        Args:
            tableColumnCount:Tablecolumn count.
            tableRowCount:Tablerow count.
        """
        GetDllLibPpt().IShape_InsertTable.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().IShape_InsertTable,self.Ptr, tableColumnCount,tableRowCount)

    @dispatch

    def InsertPicture(self ,stream:Stream):
        """
        Insert a picture into placeholder shape from stream.
        Args:
            stream:the picture stream.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().IShape_InsertPicture.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().IShape_InsertPicture,self.Ptr, intPtrstream)

    @dispatch

    def InsertPicture(self ,filepath:str):
        """
        Insert a picture into placeholder shape.
        Args:
            filepath:Picture file path.
        """
        
        filepathPtr = StrToPtr(filepath)
        GetDllLibPpt().IShape_InsertPictureF.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IShape_InsertPictureF,self.Ptr,filepathPtr)

    @property

    def Id(self)->'int':
        """
        the identity number of shape.
        """
        GetDllLibPpt().IShape_get_Id.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Id.restype=c_int
        shapeId = CallCFunction(GetDllLibPpt().IShape_get_Id,self.Ptr)
        #ret = None if intPtr==None else UInt32(intPtr)
        return shapeId



    def ReplaceTextWithRegex(self ,regex:'Regex',newValue:str):
        """
        Replaces text in the shape using regular expression matching.
        Args:
            regex: Regex object defining match pattern
            newValue: Replacement text
        """
        intPtrregex:c_void_p = regex.Ptr

        newValuePtr = StrToPtr(newValue)
        GetDllLibPpt().IShape_ReplaceTextWithRegex.argtypes=[c_void_p ,c_void_p,c_char_p]
        CallCFunction(GetDllLibPpt().IShape_ReplaceTextWithRegex,self.Ptr, intPtrregex,newValuePtr)



    def SaveAsImage(self)->'Stream':
        """
        Renders the shape as an image stream.
        Returns:
            Stream: Image data stream.
        """
        GetDllLibPpt().IShape_SaveAsImage.argtypes=[c_void_p]
        GetDllLibPpt().IShape_SaveAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_SaveAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    def SaveAsSvg(self)->'Stream':
        """
        Save the shape to SVG format.
        returns:
                A byte array of SVG file-stream.
        """
        GetDllLibPpt().IShape_SaveAsSvg.argtypes=[c_void_p]
        GetDllLibPpt().IShape_SaveAsSvg.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_SaveAsSvg,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret

    def SaveAsSvgInSlide(self)->'Stream':
        """
        Save the shape to SVG format.
        returns:
                A byte array of SVG file-stream.
        """
        GetDllLibPpt().IShape_SaveAsSvgInSlide.argtypes=[c_void_p]
        GetDllLibPpt().IShape_SaveAsSvgInSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_SaveAsSvgInSlide,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret
