from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Shape (  PptObject, IActiveSlide, IActivePresentation, IShape) :
    """
    Represents a shape on a slide. Provides properties and methods to manipulate 
    visual elements within presentation slides, including positioning, formatting, 
    and content insertion capabilities.
    """
    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide containing this shape.
        
        Returns:
            ActiveSlide: Parent slide object.
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().Shape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation containing this shape.
        
        Returns:
            Presentation: Parent presentation object.
        """
        GetDllLibPpt().Shape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


#
#    def ReplaceTextWithRegex(self ,regex:'Regex',newValue:str):
#        """
#    <summary>
#        Replace text in shape with regex.
#    </summary>
#        """
#        intPtrregex:c_void_p = regex.Ptr
#
#        GetDllLibPpt().Shape_ReplaceTextWithRegex.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        CallCFunction(GetDllLibPpt().Shape_ReplaceTextWithRegex,self.Ptr, intPtrregex,newValue)



    def SaveAsImage(self)->'Stream':
        """
        Renders the shape as an image stream.
        
        Returns:
            Stream: Image data stream.
        """
        GetDllLibPpt().Shape_SaveAsImage.argtypes=[c_void_p]
        GetDllLibPpt().Shape_SaveAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_SaveAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this shape equals another object.
        
        Args:
            obj: Object to compare with.
            
        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Shape_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Shape_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Shape_Equals,self.Ptr, intPtrobj)
        return ret

    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is a placeholder.
        
        Returns:
            bool: True if placeholder, False otherwise.
        """
        GetDllLibPpt().Shape_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Shape_get_IsPlaceholder,self.Ptr)
        return ret

    @property
    def IsTextBox(self)->bool:
        """
        Indicates whether the shape is a text box.
        
        Returns:
            bool: True if text box, False otherwise.
        """
        GetDllLibPpt().Shape_get_IsTextBox.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_IsTextBox.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Shape_get_IsTextBox,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets placeholder properties if shape is a placeholder.
        
        Returns:
            Placeholder: Placeholder object or None.
        """
        GetDllLibPpt().Shape_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
        Converts placeholder shape to regular shape by removing placeholder properties.
        """
        GetDllLibPpt().Shape_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Shape_RemovePlaceholder,self.Ptr)


    def InsertVideo(self ,filepath:str):
        """
        Inserts video content into placeholder shape.
        
        Args:
            filepath: Path to video file.
        """
        
        filepathPtr = StrToPtr(filepath)
        GetDllLibPpt().Shape_InsertVideo.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Shape_InsertVideo,self.Ptr,filepathPtr)


    def InsertSmartArt(self ,smartArtLayoutType:'SmartArtLayoutType'):
        """
        Inserts SmartArt diagram into placeholder shape.
        
        Args:
            smartArtLayoutType: Type of SmartArt layout.
        """
        enumsmartArtLayoutType:c_int = smartArtLayoutType.value

        GetDllLibPpt().Shape_InsertSmartArt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().Shape_InsertSmartArt,self.Ptr, enumsmartArtLayoutType)


    def InsertChart(self ,type:'ChartType'):
        """
        Inserts chart into placeholder shape.
        
        Args:
            type: Type of chart to insert.
        """
        enumtype:c_int = type.value

        GetDllLibPpt().Shape_InsertChart.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().Shape_InsertChart,self.Ptr, enumtype)


    def InsertTable(self ,tableColumnCount:int,tableRowCount:int):
        """
        Inserts table into placeholder shape.
        
        Args:
            tableColumnCount: Number of table columns.
            tableRowCount: Number of table rows.
        """
        
        GetDllLibPpt().Shape_InsertTable.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().Shape_InsertTable,self.Ptr, tableColumnCount,tableRowCount)

    @dispatch

    def InsertPicture(self ,stream:Stream):
        """
        Inserts picture from stream into placeholder shape.
        
        Args:
            stream: Image data stream.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().Shape_InsertPicture.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Shape_InsertPicture,self.Ptr, intPtrstream)

    @dispatch

    def InsertPicture(self ,filepath:str):
        """
        Inserts picture from file into placeholder shape.
        
        Args:
            filepath: Path to image file.
        """
        
        filepathPtr = StrToPtr(filepath)
        GetDllLibPpt().Shape_InsertPictureF.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Shape_InsertPictureF,self.Ptr,filepathPtr)

    @property

    def TagsList(self)->'TagCollection':
        """
        Gets collection of metadata tags associated with shape.
        
        Returns:
            TagCollection: Shape metadata tags.
        """
        GetDllLibPpt().Shape_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    

    @property
    def DrawIndicatedShape(self)->bool:
        """
        Gets/sets whether to display the shape indicator.
        
        Returns:
            bool: True to show indicator, False to hide.
        """
        GetDllLibPpt().Shape_get_DrawIndicatedShape.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_DrawIndicatedShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Shape_get_DrawIndicatedShape,self.Ptr)
        return ret

    @DrawIndicatedShape.setter
    def DrawIndicatedShape(self, value:bool):
        GetDllLibPpt().Shape_set_DrawIndicatedShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Shape_set_DrawIndicatedShape,self.Ptr, value)

    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets/sets positioning and sizing properties.
        
        Returns:
            GraphicFrame: Position and size properties.
        """
        GetDllLibPpt().Shape_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().Shape_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Shape_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets line formatting properties.
        
        Returns:
            TextLineFormat: Line style properties.
        """
        GetDllLibPpt().Shape_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets 3D effect properties.
        
        Returns:
            FormatThreeD: 3D formatting properties.
        """
        GetDllLibPpt().Shape_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets special visual effect properties.
        
        Returns:
            EffectDag: Visual effects properties.
        """
        GetDllLibPpt().Shape_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill formatting properties.
        
        Returns:
            FillFormat: Fill style properties.
        """
        GetDllLibPpt().Shape_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets/sets hyperlink for mouse click interaction.
        
        Returns:
            ClickHyperlink: Click action hyperlink.
        """
        GetDllLibPpt().Shape_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().Shape_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Shape_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets/sets hyperlink for mouse hover interaction.
        
        Returns:
            ClickHyperlink: Mouseover action hyperlink.
        """
        GetDllLibPpt().Shape_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().Shape_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Shape_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Gets/sets shape visibility.
        
        Returns:
            bool: True if hidden, False if visible.
        """
        GetDllLibPpt().Shape_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Shape_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().Shape_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Shape_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets parent slide containing this shape.
        
        Returns:
            ActiveSlide: Parent slide object.
        """
        GetDllLibPpt().Shape_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Shape_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets/sets stacking order position (0=back, highest=front).
        
        Returns:
            int: Current z-order position.
        """
        GetDllLibPpt().Shape_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Shape_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().Shape_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Shape_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets/sets rotation angle in degrees.
        
        Returns:
            float: Current rotation angle.
        """
        GetDllLibPpt().Shape_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Shape_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().Shape_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Shape_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets/sets horizontal position from left edge.
        
        Returns:
            float: X-coordinate position.
        """
        GetDllLibPpt().Shape_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Shape_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().Shape_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Shape_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets/sets vertical position from top edge.
        
        Returns:
            float: Y-coordinate position.
        """
        GetDllLibPpt().Shape_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Shape_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().Shape_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Shape_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets/sets shape width.
        
        Returns:
            float: Current width.
        """
        GetDllLibPpt().Shape_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Shape_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().Shape_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Shape_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets/sets shape height.
        
        Returns:
            float: Current height.
        """
        GetDllLibPpt().Shape_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Shape_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().Shape_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Shape_set_Height,self.Ptr, value)

    @property

    def Id(self)->'int':
        """
        Gets unique identifier for shape.
        
        Returns:
            int: Unique shape ID.
        """
        GetDllLibPpt().Shape_get_Id.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Id.restype=c_int
        shapeId = CallCFunction(GetDllLibPpt().Shape_get_Id,self.Ptr)
        return shapeId



    def SetShapeAlignment(self ,shapeAlignment:'ShapeAlignment'):
        """
        Sets alignment relative to other shapes.
        
        Args:
            shapeAlignment: Alignment type to apply.
        """
        enumshapeAlignment:c_int = shapeAlignment.value

        GetDllLibPpt().Shape_SetShapeAlignment.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().Shape_SetShapeAlignment,self.Ptr, enumshapeAlignment)


    def SetShapeArrange(self ,shapeArrange:'ShapeArrange'):
        """
        Sets arrangement relative to other shapes.
        
        Args:
            shapeArrange: Arrangement type to apply.
        """
        enumshapeArrange:c_int = shapeArrange.value

        GetDllLibPpt().Shape_SetShapeArrange.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().Shape_SetShapeArrange,self.Ptr, enumshapeArrange)

    @property

    def AlternativeText(self)->str:
        """
        Gets/sets accessibility description text.
        
        Returns:
            str: Alternative text description.
        """
        GetDllLibPpt().Shape_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Shape_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Shape_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Shape_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def AlternativeTitle(self)->str:
        """
        Gets/sets accessibility title text.
        
        Returns:
            str: Alternative title text.
        """
        GetDllLibPpt().Shape_get_AlternativeTitle.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_AlternativeTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Shape_get_AlternativeTitle,self.Ptr))
        return ret


    @AlternativeTitle.setter
    def AlternativeTitle(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Shape_set_AlternativeTitle.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Shape_set_AlternativeTitle,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets/sets display name for shape.
        
        Returns:
            str: Current shape name.
        """
        GetDllLibPpt().Shape_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().Shape_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Shape_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Shape_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Shape_set_Name,self.Ptr,valuePtr)

