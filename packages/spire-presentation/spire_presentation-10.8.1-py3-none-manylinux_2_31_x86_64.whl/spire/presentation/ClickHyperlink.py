from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ClickHyperlink (SpireObject) :
    """
    Represents a hyperlink associated with a non-placeholder shape or text.
    """
    @dispatch
    def __init__(self):
        """Initializes a new instance of ClickHyperlink."""
        GetDllLibPpt().ClickHyperlink_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_Create)
        super(ClickHyperlink, self).__init__(intPtr)

    @dispatch
    def __init__(self,hyperlinkUrl:str):
        """
        Initializes a new instance with a URL hyperlink.

        Args:
            hyperlinkUrl (str): The URL to link to.
        """
        hyperlinkUrlPtr = StrToPtr(hyperlinkUrl)
        GetDllLibPpt().ClickHyperlink_Create.argtypes=[c_char_p]
        GetDllLibPpt().ClickHyperlink_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_Create,hyperlinkUrlPtr)
        super(ClickHyperlink, self).__init__(intPtr)

    @dispatch
    def __init__(self,targetSlide:'ISlide'):
        """
        Initializes a new instance with a slide hyperlink.

        Args:
            targetSlide (ISlide): The slide to link to.
        """
        GetDllLibPpt().ClickHyperlink_Create_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_Create_Slide.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_Create_Slide,targetSlide.Ptr)
        super(ClickHyperlink, self).__init__(intPtr)

    @staticmethod

    def get_NoAction()->'ClickHyperlink':
        """
        Gets a special "do nothing" hyperlink.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_NoAction.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_NoAction.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_NoAction)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def get_NextSlide()->'ClickHyperlink':
        """
        Gets a hyperlink to the next slide.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_NextSlide.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_NextSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_NextSlide)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def get_PreviousSlide()->'ClickHyperlink':
        """
        Gets a hyperlink to the previous slide.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_PreviousSlide.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_PreviousSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_PreviousSlide)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def get_FirstSlide()->'ClickHyperlink':
        """
        Gets a hyperlink to the first slide.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_FirstSlide.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_FirstSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_FirstSlide)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def get_LastSlide()->'ClickHyperlink':
        """
        Gets a hyperlink to the last slide.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_LastSlide.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_LastSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_LastSlide)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def get_LastVievedSlide()->'ClickHyperlink':
        """
        Gets a hyperlink to the last viewed slide.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_LastVievedSlide.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_LastVievedSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_LastVievedSlide)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def get_EndShow()->'ClickHyperlink':
        """
        Gets a hyperlink that ends the slide show.

        Returns:
            ClickHyperlink: Readonly hyperlink instance.
        """
        #GetDllLibPpt().ClickHyperlink_get_EndShow.argtypes=[]
        GetDllLibPpt().ClickHyperlink_get_EndShow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_EndShow)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def GetOtherPowerPointPresentation(filePath:str)->'ClickHyperlink':
        """
        Creates a hyperlink to another PowerPoint presentation.

        Args:
            filePath (str): Full path to the target file.

        Returns:
            ClickHyperlink: New hyperlink instance.
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ClickHyperlink_GetOtherPowerPointPresentation.argtypes=[ c_char_p]
        GetDllLibPpt().ClickHyperlink_GetOtherPowerPointPresentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_GetOtherPowerPointPresentation,filePathPtr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @staticmethod

    def GetOtherFiles(filePath:str)->'ClickHyperlink':
        """
        Creates a hyperlink to other files.

        Args:
            filePath (str): Full path to the target file.

        Returns:
            ClickHyperlink: New hyperlink instance.
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ClickHyperlink_GetOtherFiles.argtypes=[ c_char_p]
        GetDllLibPpt().ClickHyperlink_GetOtherFiles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_GetOtherFiles,filePathPtr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @property

    def Address(self)->str:
        """
        Gets or sets the URL address.

        Returns:
            str: The internet address.
        """
        GetDllLibPpt().ClickHyperlink_get_Address.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_Address.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ClickHyperlink_get_Address,self.Ptr))
        return ret


    @Address.setter
    def Address(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ClickHyperlink_set_Address.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_Address,self.Ptr,valuePtr)

    @property
    def InvalidUrl(self)->str:
        """Gets or sets the invalid URL (internal use)."""
        GetDllLibPpt().ClickHyperlink_get_InvalidUrl.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_InvalidUrl.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ClickHyperlink_get_InvalidUrl,self.Ptr))
        return ret


    @InvalidUrl.setter
    def InvalidUrl(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ClickHyperlink_set_InvalidUrl.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_InvalidUrl,self.Ptr,valuePtr)

    @property

    def Action(self)->str:
        """Gets or sets the action type (internal use)."""
        GetDllLibPpt().ClickHyperlink_get_Action.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_Action.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ClickHyperlink_get_Action,self.Ptr))
        return ret


    @Action.setter
    def Action(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ClickHyperlink_set_Action.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_Action,self.Ptr,valuePtr)

    @property

    def ActionType(self)->'HyperlinkActionType':
        """
        Gets the type of hyperlink action.

        Returns:
            HyperlinkActionType: Readonly enum value.
        """
        GetDllLibPpt().ClickHyperlink_get_ActionType.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_ActionType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_get_ActionType,self.Ptr)
        objwraped = HyperlinkActionType(ret)
        return objwraped

    @property

    def TargetSlide(self)->'ISlide':
        """
        Gets the target slide if hyperlink targets a slide.

        Returns:
            ISlide: Readonly slide object.
        """
        from spire.presentation.ISlide import ISlide
        GetDllLibPpt().ClickHyperlink_get_TargetSlide.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_TargetSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ClickHyperlink_get_TargetSlide,self.Ptr)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @property

    def TargetFrame(self)->str:
        """
        Gets or sets the target frame within HTML frameset.

        Returns:
            str: Target frame name.
        """
        GetDllLibPpt().ClickHyperlink_get_TargetFrame.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_TargetFrame.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ClickHyperlink_get_TargetFrame,self.Ptr))
        return ret


    @TargetFrame.setter
    def TargetFrame(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ClickHyperlink_set_TargetFrame.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_TargetFrame,self.Ptr,valuePtr)

    @property

    def Tooltip(self)->str:
        """
        Gets or sets the ScreenTip text.

        Returns:
            str: Tooltip text.
        """
        GetDllLibPpt().ClickHyperlink_get_Tooltip.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_Tooltip.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ClickHyperlink_get_Tooltip,self.Ptr))
        return ret


    @Tooltip.setter
    def Tooltip(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ClickHyperlink_set_Tooltip.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_Tooltip,self.Ptr,valuePtr)

    @property
    def History(self)->bool:
        """
        Gets or sets whether to add target to history list.

        Returns:
            bool: True if target should be added to history.
        """
        GetDllLibPpt().ClickHyperlink_get_History.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_History.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_get_History,self.Ptr)
        return ret

    @History.setter
    def History(self, value:bool):
        GetDllLibPpt().ClickHyperlink_set_History.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_History,self.Ptr, value)

    @property
    def IsHighlightClick(self)->bool:
        """
        Gets or sets whether to highlight on click.

        Returns:
            bool: True if should highlight on click.
        """
        GetDllLibPpt().ClickHyperlink_get_IsHighlightClick.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_IsHighlightClick.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_get_IsHighlightClick,self.Ptr)
        return ret

    @IsHighlightClick.setter
    def IsHighlightClick(self, value:bool):
        """
        Sets whether to highlight on click.

        Args:
            value (bool): True to enable highlight.
        """
        GetDllLibPpt().ClickHyperlink_set_IsHighlightClick.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_IsHighlightClick,self.Ptr, value)

    @property
    def EndSounds(self)->bool:
        """
        Gets or sets whether to stop sounds on click.

        Returns:
            bool: True if sounds should stop.
        """
        GetDllLibPpt().ClickHyperlink_get_EndSounds.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_get_EndSounds.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_get_EndSounds,self.Ptr)
        return ret

    @EndSounds.setter
    def EndSounds(self, value:bool):
        """
        Sets whether to stop sounds on click.

        Args:
            value (bool): True to stop sounds.
        """
        GetDllLibPpt().ClickHyperlink_set_EndSounds.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ClickHyperlink_set_EndSounds,self.Ptr, value)

    @dispatch

    def Equals(self ,obj:SpireObject)->bool:
        """
        Determines if two hyperlinks are equal.

        Args:
            obj (SpireObject): The hyperlink to compare.

        Returns:
            bool: True if equal.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ClickHyperlink_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ClickHyperlink_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_Equals,self.Ptr, intPtrobj)
        return ret

    @dispatch

    def Equals(self ,hlink:'ClickHyperlink')->bool:
        """
        Determines if two hyperlinks are equal.

        Args:
            hlink (ClickHyperlink): The hyperlink to compare.

        Returns:
            bool: True if equal.
        """
        intPtrhlink:c_void_p = hlink.Ptr

        GetDllLibPpt().ClickHyperlink_EqualsH.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ClickHyperlink_EqualsH.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_EqualsH,self.Ptr, intPtrhlink)
        return ret

    @staticmethod

    def op_Equality(hlink1:'ClickHyperlink',hlink2:'ClickHyperlink')->bool:
        """
        Equality operator for hyperlinks.

        Returns:
            bool: True if equal.
        """
        intPtrhlink1:c_void_p = hlink1.Ptr
        intPtrhlink2:c_void_p = hlink2.Ptr

        GetDllLibPpt().ClickHyperlink_op_Equality.argtypes=[ c_void_p,c_void_p]
        GetDllLibPpt().ClickHyperlink_op_Equality.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_op_Equality, intPtrhlink1,intPtrhlink2)
        return ret

    @staticmethod

    def op_Inequality(hlink1:'ClickHyperlink',hlink2:'ClickHyperlink')->bool:
        """
        Inequality operator for hyperlinks.

        Returns:
            bool: True if not equal.
        """
        intPtrhlink1:c_void_p = hlink1.Ptr
        intPtrhlink2:c_void_p = hlink2.Ptr

        GetDllLibPpt().ClickHyperlink_op_Inequality.argtypes=[ c_void_p,c_void_p]
        GetDllLibPpt().ClickHyperlink_op_Inequality.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_op_Inequality, intPtrhlink1,intPtrhlink2)
        return ret

    def GetHashCode(self)->int:
        """
        Gets hash code for the hyperlink.

        Returns:
            int: Hash code value.
        """
        GetDllLibPpt().ClickHyperlink_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().ClickHyperlink_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ClickHyperlink_GetHashCode,self.Ptr)
        return ret

