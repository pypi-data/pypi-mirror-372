from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Comment (  PptObject) :
    """
    Represents a comment on a presentation slide.
    """
    @property

    def Text(self)->str:
        """
        Gets or sets the text content of the comment.
        
        Returns:
            str: Comment text content.
        """
        GetDllLibPpt().Comment_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Comment_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """
        Sets the text content of the comment.
        
        Args:
            value (str): New comment text content.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Comment_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Comment_set_Text,self.Ptr,valuePtr)

    @property

    def DateTime(self)->'DateTime':
        """
        Gets or sets the creation date and time of the comment.
        
        Returns:
            DateTime: Comment creation timestamp.
        """
        GetDllLibPpt().Comment_get_DateTime.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_DateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Comment_get_DateTime,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTime.setter
    def DateTime(self, value:'DateTime'):
        """
        Sets the creation date and time of the comment.
        
        Args:
            value (DateTime): New creation timestamp.
        """
        GetDllLibPpt().Comment_set_DateTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Comment_set_DateTime,self.Ptr, value.Ptr)

    @property

    def Slide(self)->'ISlide':
        """
        Gets the parent slide containing this comment.
        
        Returns:
            ISlide: Parent slide object.
        """
        GetDllLibPpt().Comment_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Comment_get_Slide,self.Ptr)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @property

    def AuthorName(self)->str:
        """
        Gets or sets the author's display name.
        
        Returns:
            str: Comment author's name.
        """
        GetDllLibPpt().Comment_get_AuthorName.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_AuthorName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Comment_get_AuthorName,self.Ptr))
        return ret


    @AuthorName.setter
    def AuthorName(self, value:str):
        """
        Sets the author's display name.
        
        Args:
            value (str): New author name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Comment_set_AuthorName.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Comment_set_AuthorName,self.Ptr,valuePtr)

    @property

    def AuthorInitials(self)->str:
        """
        Gets or sets the author's initials.
        
        Returns:
            str: Comment author's initials.
        """
        GetDllLibPpt().Comment_get_AuthorInitials.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_AuthorInitials.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Comment_get_AuthorInitials,self.Ptr))
        return ret


    @AuthorInitials.setter
    def AuthorInitials(self, value:str):
        """
        Sets the author's initials.
        
        Args:
            value (str): New author initials.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Comment_set_AuthorInitials.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Comment_set_AuthorInitials,self.Ptr,valuePtr)

    @property
    def Left(self)->float:
        """
        Gets or sets horizontal position from slide left edge.
        
        Returns:
            float: X-coordinate in points.
        """
        GetDllLibPpt().Comment_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Comment_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        """
        Sets horizontal position from slide left edge.
        
        Args:
            value (float): New X-coordinate in points.
        """
        GetDllLibPpt().Comment_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Comment_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets vertical position from slide top edge.
        
        Returns:
            float: Y-coordinate in points.
        """
        GetDllLibPpt().Comment_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Comment_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        """
        Sets vertical position from slide top edge.
        
        Args:
            value (float): New Y-coordinate in points.
        """
        GetDllLibPpt().Comment_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Comment_set_Top,self.Ptr, value)


    def Reply(self ,author:'ICommentAuthor',reply:str,time:'DateTime'):
        """
        Adds a reply to this comment (does nothing if comment is already a reply).
        
        Args:
            author (ICommentAuthor): Author of the reply.
            reply (str): Text content of the reply.
            time (DateTime): Timestamp of the reply.
        """
        intPtrauthor:c_void_p = author.Ptr
        intPtrtime:c_void_p = time.Ptr

        replyPtr = StrToPtr(reply)
        GetDllLibPpt().Comment_Reply.argtypes=[c_void_p ,c_void_p,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().Comment_Reply,self.Ptr, intPtrauthor,replyPtr,intPtrtime)

    @property
    def IsReply(self)->bool:
        """
        Determines if the comment is a reply to another comment.
        
        Returns:
            bool: True if comment is a reply; otherwise False.
        """
        GetDllLibPpt().Comment_get_IsReply.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_IsReply.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Comment_get_IsReply,self.Ptr)
        return ret

