from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ICommentAuthor (SpireObject) :
    """
    Represents an author of comments in a presentation.
    """
    @property

    def Initials(self)->str:
        """
        Gets or sets the author's initials.
        """
        GetDllLibPpt().ICommentAuthor_get_Initials.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_Initials.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ICommentAuthor_get_Initials,self.Ptr))
        return ret


    @Initials.setter
    def Initials(self, value:str):
        """
        Sets the author's initials.

        Args:
            value: The initials string to set.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ICommentAuthor_set_Initials.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ICommentAuthor_set_Initials,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets the author's name.
        """
        GetDllLibPpt().ICommentAuthor_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ICommentAuthor_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets the author's name.

        Args:
            value: The name string to set.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ICommentAuthor_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ICommentAuthor_set_Name,self.Ptr,valuePtr)

    @property

    def CommentsList(self)->'CommentCollection':
        """
        Gets the collection of comments by this author (read-only).
        """
        GetDllLibPpt().ICommentAuthor_get_CommentsList.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_CommentsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ICommentAuthor_get_CommentsList,self.Ptr)
        ret = None if intPtr==None else CommentCollection(intPtr)
        return ret


    @property
    def LastIndex(self)->int:
        """
        Gets the last index used by this author (read-only).
        """
        GetDllLibPpt().ICommentAuthor_get_LastIndex.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_LastIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ICommentAuthor_get_LastIndex,self.Ptr)
        return ret

    @property
    def ColorIndex(self)->int:
        """
        Gets the author's color index (read-only).
        """
        GetDllLibPpt().ICommentAuthor_get_ColorIndex.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_ColorIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ICommentAuthor_get_ColorIndex,self.Ptr)
        return ret

    @property

    def Id(self)->'UInt32':
        """
        Gets the author's unique ID (read-only).
        """
        GetDllLibPpt().ICommentAuthor_get_Id.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_Id.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ICommentAuthor_get_Id,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @property

    def ExtensionList(self)->'ExtensionList':
        """
        Gets the extension list for the author (read-only).
        """
        GetDllLibPpt().ICommentAuthor_get_ExtensionList.argtypes=[c_void_p]
        GetDllLibPpt().ICommentAuthor_get_ExtensionList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ICommentAuthor_get_ExtensionList,self.Ptr)
        ret = None if intPtr==None else ExtensionList(intPtr)
        return ret


