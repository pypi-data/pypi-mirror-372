from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IAudio (  IShape) :
    """
    Represents an audio object on a slide that inherits properties from IShape.
    Provides control over audio playback settings, volume, and embedding status.
    """
    @property

    def Volume(self)->'AudioVolumeType':
        """
        Gets or sets the audio volume.
           
        """
        GetDllLibPpt().IAudio_get_Volume.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Volume.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAudio_get_Volume,self.Ptr)
        objwraped = AudioVolumeType(ret)
        return objwraped

    @Volume.setter
    def Volume(self, value:'AudioVolumeType'):
        GetDllLibPpt().IAudio_set_Volume.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAudio_set_Volume,self.Ptr, value.value)

    @property

    def PlayMode(self)->'AudioPlayMode':
        """
        Gets or sets the audio play mode.
        """
        GetDllLibPpt().IAudio_get_PlayMode.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_PlayMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAudio_get_PlayMode,self.Ptr)
        objwraped = AudioPlayMode(ret)
        return objwraped

    @PlayMode.setter
    def PlayMode(self, value:'AudioPlayMode'):
        GetDllLibPpt().IAudio_set_PlayMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAudio_set_PlayMode,self.Ptr, value.value)

    @property
    def IsLoop(self)->bool:
        """
        Indicates whether an audio is looped.
        """
        GetDllLibPpt().IAudio_get_IsLoop.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_IsLoop.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAudio_get_IsLoop,self.Ptr)
        return ret

    @IsLoop.setter
    def IsLoop(self, value:bool):
        GetDllLibPpt().IAudio_set_IsLoop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAudio_set_IsLoop,self.Ptr, value)

    @property
    def IsEmbedded(self)->bool:
        """
        Indicates whether a sound is embedded to a presentation.
           
        """
        GetDllLibPpt().IAudio_get_IsEmbedded.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_IsEmbedded.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAudio_get_IsEmbedded,self.Ptr)
        return ret

    @property

    def FileName(self)->str:
        """
        Gets or sets the name of an audio file.
        """
        GetDllLibPpt().IAudio_get_FileName.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_FileName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAudio_get_FileName,self.Ptr))
        return ret


    @FileName.setter
    def FileName(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAudio_set_FileName.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAudio_set_FileName,self.Ptr,valuePtr)

    @property

    def Data(self)->'IAudioData':
        """
        Gets or sets embedded audio data.
          
        """
        GetDllLibPpt().IAudio_get_Data.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Data.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Data,self.Ptr)
        ret = None if intPtr==None else IAudioData(intPtr)
        return ret


    @Data.setter
    def Data(self, value:'IAudioData'):
        GetDllLibPpt().IAudio_set_Data.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAudio_set_Data,self.Ptr, value.Ptr)

    @property

    def AudioCd(self)->'AudioCD':
        """
        Gets setting of CD.
    
        """
        GetDllLibPpt().IAudio_get_AudioCd.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_AudioCd.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_AudioCd,self.Ptr)
        ret = None if intPtr==None else AudioCD(intPtr)
        return ret


    @property

    def ShapeLocking(self)->'SlidePictureLocking':
        """
        Gets shape's locks.
        Readonly
        """
        GetDllLibPpt().IAudio_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else SlidePictureLocking(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """
        Returns or sets the AutoShape type.
    
        """
        GetDllLibPpt().IAudio_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAudio_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().IAudio_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAudio_set_ShapeType,self.Ptr, value.value)

    @property

    def PictureFill(self)->'PictureFillFormat':
        """
        Gets the PictureFillFormat object.
        Read-only 
        """
        GetDllLibPpt().IAudio_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def ShapeStyle(self)->'ShapeStyle':
        """
        Gets shape's style object.
        Read-only 
        """
        GetDllLibPpt().IAudio_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """
        Gets a collection of shape's adjustment values.
        Readonly 
        """
        GetDllLibPpt().IAudio_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is Placeholder.
        Read-only
        """
        GetDllLibPpt().IAudio_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAudio_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets the placeholder for a shape.
        Read-only 
        """
        GetDllLibPpt().IAudio_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the shape's tags collection.
        Read-only 
        """
        GetDllLibPpt().IAudio_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets the shape frame's properties.
        Read/write 
        """
        GetDllLibPpt().IAudio_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().IAudio_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAudio_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets the LineFormat object that contains line formatting properties for a shape.
        Read-only 
        Note: can return null for certain types of shapes which don't have line properties.
  
        """
        GetDllLibPpt().IAudio_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets the ThreeDFormat object that 3d effect properties for a shape.
        Read-only 
        Note: can return null for certain types of shapes which don't have 3d properties.
    
        """
        GetDllLibPpt().IAudio_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets the EffectFormat object which contains pixel effects applied to a shape.
        Read-only .
        Note: can return null for certain types of shapes which don't have effect properties.
    
        """
        GetDllLibPpt().IAudio_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets the FillFormat object that contains fill formatting properties for a shape.
        Read-only.
        Note: can return null for certain types of shapes which don't have fill properties.
    
        """
        GetDllLibPpt().IAudio_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse click.
           
        """
        GetDllLibPpt().IAudio_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IAudio_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAudio_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse over.
          
        """
        GetDllLibPpt().IAudio_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().IAudio_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAudio_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates whether the shape is hidden.
           
        """
        GetDllLibPpt().IAudio_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAudio_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().IAudio_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAudio_set_IsHidden,self.Ptr, value)

    @property
    def IsPlayinBackground(self)->bool:
        """
        Whether the audio plays in the background.
           
        """
        GetDllLibPpt().IAudio_get_IsPlayinBackground.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_IsPlayinBackground.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAudio_get_IsPlayinBackground,self.Ptr)
        return ret

    @IsPlayinBackground.setter
    def IsPlayinBackground(self, value:bool):
        GetDllLibPpt().IAudio_set_IsPlayinBackground.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAudio_set_IsPlayinBackground,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
            
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IAudio_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets the position of a shape in the z-order.
        Shapes[0] returns the shape at the back of the z-order,
        and Shapes[Shapes.Count - 1] returns the shape at the front of the z-order.
   
        """
        GetDllLibPpt().IAudio_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAudio_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().IAudio_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAudio_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets the number of degrees the specified shape is rotated around
        the z-axis. A positive value indicates clockwise rotation; a negative value
        indicates counterclockwise rotation.
            
        """
        GetDllLibPpt().IAudio_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAudio_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().IAudio_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAudio_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets the x-coordinate of the upper-left corner of the shape.
           
        """
        GetDllLibPpt().IAudio_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAudio_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().IAudio_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAudio_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the y-coordinate of the upper-left corner of the shape.
           
        """
        GetDllLibPpt().IAudio_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAudio_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().IAudio_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAudio_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the shape.
            
        """
        GetDllLibPpt().IAudio_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAudio_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IAudio_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAudio_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the shape.
            
        """
        GetDllLibPpt().IAudio_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAudio_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().IAudio_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAudio_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets the alternative text associated with a shape.
           
        """
        GetDllLibPpt().IAudio_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAudio_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAudio_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAudio_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets the name of a shape.
            
        """
        GetDllLibPpt().IAudio_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAudio_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAudio_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAudio_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
            
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IAudio_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent Presentation object that contains this component.

        Returns:
            Presentation: The parent presentation instance
        """
        from spire.presentation import Presentation
        GetDllLibPpt().IAudio_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudio_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property
    def HideAtShowing(self)->bool:
        """
        Indicates whether an Audio is hidden.
            
        """
        GetDllLibPpt().IAudio_get_HideAtShowing.argtypes=[c_void_p]
        GetDllLibPpt().IAudio_get_HideAtShowing.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAudio_get_HideAtShowing,self.Ptr)
        return ret

    @HideAtShowing.setter
    def HideAtShowing(self, value:bool):
        GetDllLibPpt().IAudio_set_HideAtShowing.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAudio_set_HideAtShowing,self.Ptr, value)

    def RemovePlaceholder(self):
        """
        Removes placeholder from the shape.
   
        """
        GetDllLibPpt().IAudio_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IAudio_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
        Dispose object and free resources.
    
        """
        GetDllLibPpt().IAudio_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IAudio_Dispose,self.Ptr)

