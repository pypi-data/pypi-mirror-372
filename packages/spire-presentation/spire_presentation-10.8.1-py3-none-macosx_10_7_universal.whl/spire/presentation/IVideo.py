from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IVideo (  IShape) :
    """
    Represents a video frame on a slide.

    This class provides properties and methods to manage video content
    embedded or linked to a PowerPoint slide.
    """
    @property

    def EmbedImage(self)->'IImageData':
        """
        Gets or sets the embedded preview image for the video.

        Returns:
            IImageData: The embedded preview image object.
        """
        GetDllLibPpt().IVideo_get_EmbedImage.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_EmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_EmbedImage,self.Ptr)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    @EmbedImage.setter
    def EmbedImage(self, value:'IImageData'):
        """
        Sets the embedded preview image for the video.

        Args:
            value (IImageData): The image to set as preview.
        """
        GetDllLibPpt().IVideo_set_EmbedImage.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_EmbedImage,self.Ptr, value.Ptr)

    @property
    def RewindVideo(self)->bool:
        """
        Indicates whether video automatically rewinds after playback.

        Returns:
            bool: True if video rewinds automatically, False otherwise.
        """
        GetDllLibPpt().IVideo_get_RewindVideo.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_RewindVideo.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_RewindVideo,self.Ptr)
        return ret

    @RewindVideo.setter
    def RewindVideo(self, value:bool):
        """
        Sets automatic rewind behavior after playback.

        Args:
            value (bool): True to enable auto-rewind, False to disable.
        """
        GetDllLibPpt().IVideo_set_RewindVideo.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_RewindVideo,self.Ptr, value)

    @property
    def PlayLoopMode(self)->bool:
        """
        Indicates whether video loops continuously.

        Returns:
            bool: True if looping is enabled, False otherwise.
        """
        GetDllLibPpt().IVideo_get_PlayLoopMode.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_PlayLoopMode.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_PlayLoopMode,self.Ptr)
        return ret

    @PlayLoopMode.setter
    def PlayLoopMode(self, value:bool):
        """
        Enables or disables continuous video looping.

        Args:
            value (bool): True to enable looping, False to disable.
        """
        GetDllLibPpt().IVideo_set_PlayLoopMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_PlayLoopMode,self.Ptr, value)

    @property
    def HideAtShowing(self)->bool:
        """
        Indicates whether video is hidden during playback.

        Returns:
            bool: True if hidden during playback, False otherwise.
        """
        GetDllLibPpt().IVideo_get_HideAtShowing.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_HideAtShowing.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_HideAtShowing,self.Ptr)
        return ret

    @HideAtShowing.setter
    def HideAtShowing(self, value:bool):
        """
        Sets visibility during playback.

        Args:
            value (bool): True to hide during playback, False to show.
        """
        GetDllLibPpt().IVideo_set_HideAtShowing.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_HideAtShowing,self.Ptr, value)

    @property

    def Volume(self)->'AudioVolumeType':
        """
        Gets or sets audio volume level.

        Returns:
            AudioVolumeType: The current volume level enumeration.
        """
        GetDllLibPpt().IVideo_get_Volume.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Volume.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Volume,self.Ptr)
        objwraped = AudioVolumeType(ret)
        return objwraped

    @Volume.setter
    def Volume(self, value:'AudioVolumeType'):
        """
        Sets audio volume level.

        Args:
            value (AudioVolumeType): Volume level enumeration to set.
        """
        GetDllLibPpt().IVideo_set_Volume.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_Volume,self.Ptr, value.value)

    @property

    def PlayMode(self)->'VideoPlayMode':
        """
        Gets or sets video playback behavior.

        Returns:
            VideoPlayMode: Current playback mode enumeration.
        """
        GetDllLibPpt().IVideo_get_PlayMode.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_PlayMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_PlayMode,self.Ptr)
        objwraped = VideoPlayMode(ret)
        return objwraped

    @PlayMode.setter
    def PlayMode(self, value:'VideoPlayMode'):
        """
        Sets video playback behavior.

        Args:
            value (VideoPlayMode): Playback mode enumeration to set.
        """
        GetDllLibPpt().IVideo_set_PlayMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_PlayMode,self.Ptr, value.value)

    @property
    def FullScreenMode(self)->bool:
        """
        Indicates whether video plays in full-screen mode.

        Returns:
            bool: True if full-screen mode enabled, False otherwise.
        """
        GetDllLibPpt().IVideo_get_FullScreenMode.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_FullScreenMode.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_FullScreenMode,self.Ptr)
        return ret

    @FullScreenMode.setter
    def FullScreenMode(self, value:bool):
        """
        Enables or disables full-screen playback.

        Args:
            value (bool): True for full-screen, False for windowed.
        """
        GetDllLibPpt().IVideo_set_FullScreenMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_FullScreenMode,self.Ptr, value)

    @property

    def LinkPathLong(self)->str:
        """
        Gets or sets linked video file path.

        Returns:
            str: Full path to linked video file.
        """
        GetDllLibPpt().IVideo_get_LinkPathLong.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_LinkPathLong.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IVideo_get_LinkPathLong,self.Ptr))
        return ret


    @LinkPathLong.setter
    def LinkPathLong(self, value:str):
        """
        Sets linked video file path.

        Args:
            value (str): Full path to video file.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IVideo_set_LinkPathLong.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IVideo_set_LinkPathLong,self.Ptr,valuePtr)

    @property

    def EmbeddedVideoData(self)->'VideoData':
        """
        Gets or sets embedded video object.

        Returns:
            VideoData: Embedded video data object.
        """
        GetDllLibPpt().IVideo_get_EmbeddedVideoData.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_EmbeddedVideoData.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_EmbeddedVideoData,self.Ptr)
        ret = None if intPtr==None else VideoData(intPtr)
        return ret


    @EmbeddedVideoData.setter
    def EmbeddedVideoData(self, value:'VideoData'):
        """
        Sets embedded video object.

        Args:
            value (VideoData): Video data object to embed.
        """
        GetDllLibPpt().IVideo_set_EmbeddedVideoData.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_EmbeddedVideoData,self.Ptr, value.Ptr)

    @property

    def ShapeLocking(self)->'SlidePictureLocking':
        """
        Gets shape locking properties (read-only).

        Returns:
            SlidePictureLocking: Locking settings object.
        """
        GetDllLibPpt().IVideo_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else SlidePictureLocking(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """
        Gets or sets AutoShape type identifier.

        Returns:
            ShapeType: Shape type enumeration.
        """
        GetDllLibPpt().IVideo_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        """
        Sets AutoShape type identifier.

        Args:
            value (ShapeType): Shape type enumeration to set.
        """
        GetDllLibPpt().IVideo_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_ShapeType,self.Ptr, value.value)

    @property

    def PictureFill(self)->'PictureFillFormat':
        """
        Gets picture fill properties (read-only).

        Returns:
            PictureFillFormat: Picture fill settings object.
        """
        GetDllLibPpt().IVideo_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def ShapeStyle(self)->'ShapeStyle':
        """
        Gets shape style properties (read-only).

        Returns:
            ShapeStyle: Shape style object.
        """
        GetDllLibPpt().IVideo_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """
        Gets shape adjustment values (read-only).

        Returns:
            ShapeAdjustCollection: Collection of adjustment values.
        """
        GetDllLibPpt().IVideo_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates if shape is a placeholder (read-only).

        Returns:
            bool: True if placeholder, False otherwise.
        """
        GetDllLibPpt().IVideo_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets placeholder properties (read-only).

        Returns:
            Placeholder: Placeholder object.
        """
        GetDllLibPpt().IVideo_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets shape tags (read-only).

        Returns:
            TagCollection: Collection of tags.
        """
        GetDllLibPpt().IVideo_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets shape frame properties.

        Returns:
            GraphicFrame: Frame properties object.
        """
        GetDllLibPpt().IVideo_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        """
        Sets shape frame properties.

        Args:
            value (GraphicFrame): Frame properties to set.
        """

        GetDllLibPpt().IVideo_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets line formatting properties (read-only).

        Returns:
            TextLineFormat: Line format object.
        """
        GetDllLibPpt().IVideo_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets 3D effect properties (read-only).

        Returns:
            FormatThreeD: 3D format settings object.
        """
        GetDllLibPpt().IVideo_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets pixel effect properties (read-only).

        Returns:
            EffectDag: Special effects object.
        """
        GetDllLibPpt().IVideo_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill formatting properties (read-only).

        Returns:
            FillFormat: Fill format object.
        """
        GetDllLibPpt().IVideo_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets mouse-click hyperlink.

        Returns:
            ClickHyperlink: Hyperlink object.
        """
        GetDllLibPpt().IVideo_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        """
        Sets mouse-click hyperlink.

        Args:
            value (ClickHyperlink): Hyperlink to assign.
        """
        GetDllLibPpt().IVideo_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets mouse-over hyperlink.

        Returns:
            ClickHyperlink: Hyperlink object.
        """
        GetDllLibPpt().IVideo_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        """
        Sets mouse-over hyperlink.

        Args:
            value (ClickHyperlink): Hyperlink to assign.
        """
        GetDllLibPpt().IVideo_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates if shape is hidden.

        Returns:
            bool: True if hidden, False otherwise.
        """
        GetDllLibPpt().IVideo_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        """
        Sets shape visibility.

        Args:
            value (bool): True to hide, False to show.
        """
        GetDllLibPpt().IVideo_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets parent slide (read-only).

        Returns:
            ActiveSlide: Parent slide object.
        """
        GetDllLibPpt().IVideo_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets z-order position.

        Returns:
            int: Position in z-order (0=back).
        """
        GetDllLibPpt().IVideo_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        """
        Sets z-order position.

        Args:
            value (int): New z-order position.
        """
        GetDllLibPpt().IVideo_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets rotation angle (degrees).

        Returns:
            float: Rotation angle in degrees.
        """
        GetDllLibPpt().IVideo_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        """
        Sets rotation angle.

        Args:
            value (float): Rotation angle in degrees.
        """
        GetDllLibPpt().IVideo_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets left position.

        Returns:
            float: X-coordinate of upper-left corner.
        """
        GetDllLibPpt().IVideo_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        """
        Sets left position.

        Args:
            value (float): New X-coordinate value.
        """
        GetDllLibPpt().IVideo_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets top position.

        Returns:
            float: Y-coordinate of upper-left corner.
        """
        GetDllLibPpt().IVideo_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        """
        Sets top position.

        Args:
            value (float): New Y-coordinate value.
        """
        GetDllLibPpt().IVideo_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets shape width.

        Returns:
            float: Current width value.
        """
        GetDllLibPpt().IVideo_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        """
        Sets shape width.

        Args:
            value (float): New width value.
        """
        GetDllLibPpt().IVideo_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets shape height.

        Returns:
            float: Current height value.
        """
        GetDllLibPpt().IVideo_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        """
        Sets shape height.

        Args:
            value (float): New height value.
        """
        GetDllLibPpt().IVideo_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets alternative text.

        Returns:
            str: Alternative text description.
        """
        GetDllLibPpt().IVideo_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IVideo_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        """
        Sets alternative text.

        Args:
            value (str): New alternative text.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IVideo_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IVideo_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets shape name.

        Returns:
            str: Current shape name.
        """
        GetDllLibPpt().IVideo_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IVideo_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets shape name.

        Args:
            value (str): New shape name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IVideo_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IVideo_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets parent slide (read-only).

        Returns:
            ActiveSlide: Parent slide object.
        """
        GetDllLibPpt().IVideo_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets parent presentation (read-only).

        Returns:
            Presentation: Parent presentation object.
        """
        GetDllLibPpt().IVideo_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
        Removes placeholder properties from shape.
        """
        GetDllLibPpt().IVideo_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
        Releases resources associated with the object.
        """
        GetDllLibPpt().IVideo_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_Dispose,self.Ptr)

