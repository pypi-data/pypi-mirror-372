from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ParagraphList (  IActiveSlide) :
    """
    Represents a collection of paragraphs in a presentation slide.
    """

    def AddFromHtml(self ,htmlText:str):
        """
        Adds text content to the collection from HTML-formatted text.
        
        Args:
            htmlText: HTML-formatted string to add as paragraphs
        """
        
        htmlTextPtr = StrToPtr(htmlText)
        GetDllLibPpt().ParagraphList_AddFromHtml.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ParagraphList_AddFromHtml,self.Ptr,htmlTextPtr)

    @property
    def Count(self)->int:
        """
        Gets the number of paragraphs contained in the collection.
        
        Returns:
            int: The actual number of paragraphs in the collection
        """
        GetDllLibPpt().ParagraphList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        """
        Gets the paragraph at the specified index position.
        
        Args:
            index: Zero-based index of the paragraph to retrieve
            
        Returns:
            TextParagraph: The paragraph at the specified index
            
        Raises:
            StopIteration: If index is out of range
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().ParagraphList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ParagraphList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret

    def get_Item(self ,index:int)->'TextParagraph':
        """
        Gets the paragraph at the specified index position.
        
        Args:
            index: Zero-based index of the paragraph to retrieve
            
        Returns:
            TextParagraph: The paragraph at the specified index
        """
        
        GetDllLibPpt().ParagraphList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ParagraphList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret

    
    def Append(self ,value:'TextParagraph')->int:
        """
        Adds a paragraph to the end of the collection.
        
        Args:
            value: The paragraph to add to the collection
            
        Returns:
            int: The index position where the paragraph was added
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphList_Append,self.Ptr, intPtrvalue)
        return ret

    
    def AppendCollection(self ,value:'ParagraphCollection')->int:
        """
        Adds all paragraphs from another collection to the end of this collection.
        
        Args:
            value: The source collection containing paragraphs to add
            
        Returns:
            int: The starting index where paragraphs were added, or -1 if no paragraphs were added
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_AppendV.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphList_AppendV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphList_AppendV,self.Ptr, intPtrvalue)
        return ret

    @dispatch

    def Insert(self ,index:int,value:'TextParagraph'):
        """
        Inserts a paragraph at the specified index position.
        
        Args:
            index: Zero-based index at which to insert the paragraph
            value: The paragraph to insert
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphList_Insert,self.Ptr, index,intPtrvalue)

    @dispatch

    def InsertCollection(self ,index:int,value:'ParagraphCollection'):
        """
        Inserts all paragraphs from another collection at the specified index position.
        
        Args:
            index: Zero-based index at which to insert paragraphs
            value: The source collection containing paragraphs to insert
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_InsertIV.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphList_InsertIV,self.Ptr, index,intPtrvalue)

    def Clear(self):
        """
        Removes all paragraphs from the collection.
        """
        GetDllLibPpt().ParagraphList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphList_Clear,self.Ptr)


    def RemoveAt(self ,index:int):
        """
        Removes the paragraph at the specified index position.
        
        Args:
            index: Zero-based index of the paragraph to remove
        """
        
        GetDllLibPpt().ParagraphList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ParagraphList_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the paragraph collection.
        
        Returns:
            IEnumerator: An enumerator that can be used to iterate through the collection
        """
        GetDllLibPpt().ParagraphList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current object.
        
        Args:
            obj: The object to compare with the current object
            
        Returns:
            bool: True if the specified object is equal to the current object; otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ParagraphList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphList_Equals,self.Ptr, intPtrobj)
        return ret

