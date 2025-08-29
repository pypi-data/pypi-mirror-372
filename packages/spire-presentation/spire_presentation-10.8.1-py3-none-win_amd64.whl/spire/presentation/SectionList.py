from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SectionList (SpireObject) :
    """
    Represents a collection of sections in a presentation.
    Manages the organization and ordering of slide groups.
    """
    @property
    def Count(self)->int:
        """
        Gets the total number of sections in the collection.
        
        Returns:
            int: Count of sections.
        """
        GetDllLibPpt().SectionList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SectionList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SectionList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'Section':
        """
        Retrieves a section by its index position.
        
        Args:
            index: Zero-based section index.
            
        Returns:
            Section: Section object at specified position.
        """
        
        GetDllLibPpt().SectionList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SectionList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def Add(self ,sectionName:str,slide:'ISlide')->'Section':
        """
        Creates a new section containing a slide.
        Note: Only works with .pptx/.potx file formats.
        
        Args:
            sectionName: Name for the new section.
            slide: Initial slide to include.
            
        Returns:
            Section: Newly created section object.
        """
        intPtrslide:c_void_p = slide.Ptr

        sectionNamePtr = StrToPtr(sectionName)
        GetDllLibPpt().SectionList_Add.argtypes=[c_void_p ,c_char_p,c_void_p]
        GetDllLibPpt().SectionList_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_Add,self.Ptr,sectionNamePtr,intPtrslide)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def Insert(self ,sectionIndex:int,sectionName:str)->'Section':
        """
        Inserts a new section at the specified position.
        
        Args:
            sectionIndex: Target insertion position.
            sectionName: Name for the new section.
            
        Returns:
            Section: Newly created section object.
        """
        
        sectionNamePtr = StrToPtr(sectionName)
        GetDllLibPpt().SectionList_Insert.argtypes=[c_void_p ,c_int,c_char_p]
        GetDllLibPpt().SectionList_Insert.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_Insert,self.Ptr, sectionIndex,sectionNamePtr)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def Append(self ,sectionName:str)->'Section':
        """
        Adds a new section to the end of the collection.
        
        Args:
            sectionName: Name for the new section.
            
        Returns:
            Section: Newly created section object.
        """
        sectionNamePtr = StrToPtr(sectionName)
        GetDllLibPpt().SectionList_Append.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().SectionList_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_Append,self.Ptr,sectionNamePtr)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def IndexOf(self ,section:'Section')->int:
        """
        Gets the index position of a section.
        
        Args:
            section: Target section object.
            
        Returns:
            int: Zero-based index position.
        """
        intPtrsection:c_void_p = section.Ptr

        GetDllLibPpt().SectionList_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SectionList_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SectionList_IndexOf,self.Ptr, intPtrsection)
        return ret


    def MoveSlide(self ,section:'Section',index:int,slide:'ISlide'):
        """
        Moves a slide within a specific section.
        
        Args:
            section: Target section containing the slide.
            index: New position index for the slide.
            slide: Slide object to relocate.
        """
        intPtrsection:c_void_p = section.Ptr
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SectionList_MoveSlide.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().SectionList_MoveSlide,self.Ptr, intPtrsection,index,intPtrslide)


    def InsertSlide(self ,section:'Section',index:int,slide:'ISlide')->'ISlide':
        """
        Inserts a slide into a section at a specific position.
        
        Args:
            section: Target section for insertion.
            index: Insertion position index.
            slide: Slide object to insert.
            
        Returns:
            ISlide: Inserted slide object.
        """
        intPtrsection:c_void_p = section.Ptr
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SectionList_InsertSlide.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
        GetDllLibPpt().SectionList_InsertSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_InsertSlide,self.Ptr, intPtrsection,index,intPtrslide)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret



    def RemoveSlide(self ,section:'Section',index:int):
        """
        Removes a slide from a section.
        
        Args:
            section: Section containing the slide.
            index: Position index of slide to remove.
        """
        intPtrsection:c_void_p = section.Ptr

        GetDllLibPpt().SectionList_RemoveSlide.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt().SectionList_RemoveSlide,self.Ptr, intPtrsection,index)


    def RemoveAt(self ,index:int):
        """
        Deletes a section by its index position.
        
        Args:
            index: Position index of section to remove.
        """
        GetDllLibPpt().SectionList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().SectionList_RemoveAt,self.Ptr, index)

    def RemoveAll(self):
        """
        Clears all sections from the collection.
        """
        GetDllLibPpt().SectionList_RemoveAll.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().SectionList_RemoveAll,self.Ptr)

