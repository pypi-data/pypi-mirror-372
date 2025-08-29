from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommentAuthorList (SpireObject) :
    """
    Manages a collection of comment authors in a presentation.
    
    Attributes:
        Count (int): Number of authors in the collection.
        Presentation (Presentation): Parent presentation object containing this collection.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of authors in the collection.
        
        Returns:
            int: Number of comment authors.
        """
        GetDllLibPpt().CommentAuthorList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        """
        Gets the author at the specified index using indexer syntax.
        
        Args:
            index (int): Zero-based index of the author.
        
        Returns:
            ICommentAuthor: Comment author object.
        """
        if index >= self.Count:
            raise StopIteration
         
        GetDllLibPpt().CommentAuthorList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentAuthorList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ICommentAuthor(intPtr)
        return ret

    def get_Item(self ,index:int)->'ICommentAuthor':
        """
        Gets the author at the specified index.
        
        Args:
            index (int): Zero-based index of the author.
        
        Returns:
            ICommentAuthor: Comment author object.
        """
        
        GetDllLibPpt().CommentAuthorList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentAuthorList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ICommentAuthor(intPtr)
        return ret



    def AddAuthor(self ,name:str,initials:str)->'ICommentAuthor':
        """
        Adds a new author to the collection.
        
        Args:
            name (str): Display name of the new author.
            initials (str): Initials of the new author.
        
        Returns:
            ICommentAuthor: Newly created comment author object.
        """
        namePtr = StrToPtr(name)
        initialsPtr = StrToPtr(initials)
        GetDllLibPpt().CommentAuthorList_AddAuthor.argtypes=[c_void_p ,c_char_p,c_char_p]
        GetDllLibPpt().CommentAuthorList_AddAuthor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_AddAuthor,self.Ptr,namePtr,initialsPtr)
        ret = None if intPtr==None else ICommentAuthor(intPtr)
        return ret


#
#    def ToArray(self)->List['ICommentAuthor']:
#        """
#
#        """
#        GetDllLibPpt().CommentAuthorList_ToArray.argtypes=[c_void_p]
#        GetDllLibPpt().CommentAuthorList_ToArray.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().CommentAuthorList_ToArray,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, ICommentAuthor)
#        return ret



    def FindByName(self ,name:str)->List['ICommentAuthor']:
       """
        Finds authors by their display name.
        
        Args:
            name (str): Name to search for.
        
        Returns:
            List[ICommentAuthor]: List of matching comment authors.
        """
       namePtr = StrToPtr(name)
       GetDllLibPpt().CommentAuthorList_FindByName.argtypes=[c_void_p ,c_char_p]
       GetDllLibPpt().CommentAuthorList_FindByName.restype=IntPtrArray
       intPtrArray = CallCFunction(GetDllLibPpt().CommentAuthorList_FindByName,self.Ptr, namePtr)
       ret = GetObjVectorFromArray(intPtrArray, ICommentAuthor)
       return ret


#
#    def FindByNameAndInitials(self ,name:str,initials:str)->List['ICommentAuthor']:
#        """
#    <summary>
#        Find author in a collection by name and initials
#    </summary>
#    <param name="name">Name of an author to find.</param>
#    <param name="initials">Initials of an author to find.</param>
#    <returns>Authors or null.</returns>
#        """
#        
#        GetDllLibPpt().CommentAuthorList_FindByNameAndInitials.argtypes=[c_void_p ,c_wchar_p,c_wchar_p]
#        GetDllLibPpt().CommentAuthorList_FindByNameAndInitials.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().CommentAuthorList_FindByNameAndInitials,self.Ptr, name,initials)
#        ret = GetObjVectorFromArray(intPtrArray, ICommentAuthor)
#        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: Enumerator object for the collection.
        """
        GetDllLibPpt().CommentAuthorList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation containing this collection.
        
        Returns:
            Presentation: Parent presentation object.
        """
        GetDllLibPpt().CommentAuthorList_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorList_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


