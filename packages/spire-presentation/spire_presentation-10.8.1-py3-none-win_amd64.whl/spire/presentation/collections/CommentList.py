from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommentList (SpireObject) :
    """
    Represents a collection of comments from a single author.
    
    Provides methods for managing comments in a presentation.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of comments in the collection.
        
        Returns:
            int: The actual number of elements in the collection.
        """
        GetDllLibPpt().CommentList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CommentList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommentList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        """
        Gets the comment at the specified index.
        
        Args:
            index: The zero-based index of the comment to retrieve
            
        Returns:
            Comment: The comment at the specified position
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().CommentList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Comment(intPtr)
        return ret

    def get_Item(self ,index:int)->'Comment':
        """
        Gets the comment at the specified index.
        
        Args:
            index: The zero-based index of the comment to retrieve
            
        Returns:
            Comment: The comment at the specified position
        """
        
        GetDllLibPpt().CommentList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Comment(intPtr)
        return ret



    def AppendComment(self ,slide:'ISlide',text:str,x:float,y:float)->'Comment':
        """
        Adds a new comment to a slide.
        
        Args:
            slide: The target slide object
            text: Text content of the new comment
            x: Horizontal position coordinate of the comment
            y: Vertical position coordinate of the comment
            
        Returns:
            Comment: The newly created comment object
        """
        intPtrslide:c_void_p = slide.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().CommentList_AppendComment.argtypes=[c_void_p ,c_void_p,c_char_p,c_float,c_float]
        GetDllLibPpt().CommentList_AppendComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_AppendComment,self.Ptr, intPtrslide,textPtr,x,y)
        ret = None if intPtr==None else Comment(intPtr)
        return ret



    def InsertComment(self ,slide:'ISlide',Index:int,text:str,x:float,y:float)->'Comment':
        """
        Inserts a new comment at the specified position.
        
        Args:
            slide: The target slide object
            index: The insertion position index
            text: Text content of the new comment
            x: Horizontal position coordinate
            y: Vertical position coordinate
            
        Returns:
            Comment: The newly created comment object
        """
        intPtrslide:c_void_p = slide.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().CommentList_InsertComment.argtypes=[c_void_p ,c_void_p,c_int,c_char_p,c_float,c_float]
        GetDllLibPpt().CommentList_InsertComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_InsertComment,self.Ptr, intPtrslide,Index,textPtr,x,y)
        ret = None if intPtr==None else Comment(intPtr)
        return ret

    def RemoveAt(self ,index:int):
        """
        Removes the comment at the specified index.
        
        Args:
            index: The zero-based index of the comment to remove
        """
        
        GetDllLibPpt().CommentList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().CommentList_RemoveAt,self.Ptr, index)


    def Remove(self ,comment:'Comment'):
        """
        Removes the specified comment from the collection.
        
        Args:
            comment: The comment object to remove
        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibPpt().CommentList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().CommentList_Remove,self.Ptr, intPtrcomment)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for iterating through the collection.
        
        Returns:
            IEnumerator: An enumerator for the entire collection
        """
        GetDllLibPpt().CommentList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CommentList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation object.
        
        Returns:
            Presentation: The parent presentation containing this comment collection.
        """
        GetDllLibPpt().CommentList_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().CommentList_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


