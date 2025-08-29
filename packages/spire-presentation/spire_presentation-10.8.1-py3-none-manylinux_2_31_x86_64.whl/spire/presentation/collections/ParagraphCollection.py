from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ParagraphCollection (  ParagraphList) :
    """
    Represents a collection of paragraphs in a presentation.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current object.
        
        Args:
            obj: The object to compare with the current object
            
        Returns:
            bool: True if the specified object is equal to the current object; otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ParagraphCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphCollection_Equals,self.Ptr, intPtrobj)
        return ret

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.
        
        Returns:
            bool: True if access is synchronized (thread-safe); otherwise False
        """
        GetDllLibPpt().ParagraphCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection
        """
        GetDllLibPpt().ParagraphCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    #def AddParagraphFromLatexMathCode(self ,latexMathCode:str)->'TextParagraph':
    #    """
    #<summary>
    #    Creat math equation from latex math code.
    #</summary>
    #<param name="latexMathCode">latex math code.</param>
    #    """
        
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromLatexMathCode.argtypes=[c_void_p ,c_wchar_p]
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromLatexMathCode.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ParagraphCollection_AddParagraphFromLatexMathCode,self.Ptr, latexMathCode)
    #    ret = None if intPtr==None else TextParagraph(intPtr)
    #    return ret



    #def AddParagraphFromMathMLCode(self ,MathMLCode:str)->'TextParagraph':
    #    """
    #<summary>
    #    Creat math equation from mathML code.
    #</summary>
    #<param name="MathMLCode">mathML code.</param>
    #    """
        
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromMathMLCode.argtypes=[c_void_p ,c_wchar_p]
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromMathMLCode.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ParagraphCollection_AddParagraphFromMathMLCode,self.Ptr, MathMLCode)
    #    ret = None if intPtr==None else TextParagraph(intPtr)
    #    return ret


