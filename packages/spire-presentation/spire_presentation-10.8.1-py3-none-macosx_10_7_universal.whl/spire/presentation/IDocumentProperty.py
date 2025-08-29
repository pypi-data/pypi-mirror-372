from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IDocumentProperty (SpireObject) :
    """
    Manages built-in and custom document properties/metadata for presentations.
    """
    @property

    def Application(self)->str:
        """
        Gets or sets the name of the application.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Application.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Application.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Application,self.Ptr))
        return ret


    @Application.setter
    def Application(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Application.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Application,self.Ptr,valuePtr)


    @property

    def MarkAsFinal(self)->bool:
        """
        Gets or sets the name of the application.
            
        """
        GetDllLibPpt().IDocumentProperty_IsMarkAsFinal.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_IsMarkAsFinal.restype= c_bool
        ret = CallCFunction(GetDllLibPpt().IDocumentProperty_IsMarkAsFinal,self.Ptr)
        return ret


    @MarkAsFinal.setter
    def MarkAsFinal(self, value:bool):
        GetDllLibPpt().IDocumentProperty_MarkAsFinal.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IDocumentProperty_MarkAsFinal,self.Ptr, value)


    @property

    def Company(self)->str:
        """
        Gets or sets the company property.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Company.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Company.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Company,self.Ptr))
        return ret


    @Company.setter
    def Company(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Company.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Company,self.Ptr,valuePtr)

    @property

    def Manager(self)->str:
        """
        Gets or sets the manager property.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Manager.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Manager.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Manager,self.Ptr))
        return ret


    @Manager.setter
    def Manager(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Manager.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Manager,self.Ptr,valuePtr)

    @property

    def Format(self)->str:
        """
        Gets or sets the intended format of a presentation.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Format.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Format.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Format,self.Ptr))
        return ret


    @Format.setter
    def Format(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Format.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Format,self.Ptr,valuePtr)

    @property
    def SharedDoc(self)->bool:
        """
        Indicates whether the presentation is shared between multiple people.
            
        """
        GetDllLibPpt().IDocumentProperty_get_SharedDoc.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_SharedDoc.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IDocumentProperty_get_SharedDoc,self.Ptr)
        return ret

    @SharedDoc.setter
    def SharedDoc(self, value:bool):
        GetDllLibPpt().IDocumentProperty_set_SharedDoc.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_SharedDoc,self.Ptr, value)

    @property

    def Template(self)->str:
        """
        Gets or sets the template of a application.
            
        """
        GetDllLibPpt().IDocumentProperty_get_Template.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Template.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Template,self.Ptr))
        return ret


    @Template.setter
    def Template(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Template.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Template,self.Ptr,valuePtr)

    @property

    def TotalEditingTime(self)->'TimeSpan':
        """
        Total editing time of a presentation.

        """
        GetDllLibPpt().IDocumentProperty_get_TotalEditingTime.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_TotalEditingTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IDocumentProperty_get_TotalEditingTime,self.Ptr)
        ret = None if intPtr==None else TimeSpan(intPtr)
        return ret


    @TotalEditingTime.setter
    def TotalEditingTime(self, value:'TimeSpan'):
        GetDllLibPpt().IDocumentProperty_set_TotalEditingTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_TotalEditingTime,self.Ptr, value.Ptr)

    @property

    def Title(self)->str:
        """
        Gets or sets the title of a presentation.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Title.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Title.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Title,self.Ptr))
        return ret


    @Title.setter
    def Title(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Title.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Title,self.Ptr,valuePtr)

    @property

    def Subject(self)->str:
        """
        Gets or sets the subject of a presentation.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Subject.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Subject.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Subject,self.Ptr))
        return ret


    @Subject.setter
    def Subject(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Subject.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Subject,self.Ptr,valuePtr)

    @property

    def Author(self)->str:
        """
        Gets or sets the author of a presentation.
           
        """
        GetDllLibPpt().IDocumentProperty_get_Author.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Author.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Author,self.Ptr))
        return ret


    @Author.setter
    def Author(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Author.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Author,self.Ptr,valuePtr)

    @property

    def Keywords(self)->str:
        """
        Gets or sets the keywords of a presentation.

        """
        GetDllLibPpt().IDocumentProperty_get_Keywords.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Keywords.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Keywords,self.Ptr))
        return ret


    @Keywords.setter
    def Keywords(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Keywords.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Keywords,self.Ptr,valuePtr)

    @property

    def Comments(self)->str:
        """
        Gets or sets the comments of a presentation.

        """
        GetDllLibPpt().IDocumentProperty_get_Comments.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Comments.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Comments,self.Ptr))
        return ret


    @Comments.setter
    def Comments(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Comments.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Comments,self.Ptr,valuePtr)

    @property

    def Category(self)->str:
        """
        Gets or sets the category of a presentation.

        """
        GetDllLibPpt().IDocumentProperty_get_Category.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Category.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_Category,self.Ptr))
        return ret


    @Category.setter
    def Category(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_Category.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Category,self.Ptr,valuePtr)

    @property

    def CreatedTime(self)->'DateTime':
        """
        Gets or sets the date when a presentation was created.
            
        """
        GetDllLibPpt().IDocumentProperty_get_CreatedTime.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_CreatedTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IDocumentProperty_get_CreatedTime,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @CreatedTime.setter
    def CreatedTime(self, value:'DateTime'):
        GetDllLibPpt().IDocumentProperty_set_CreatedTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_CreatedTime,self.Ptr, value.Ptr)

    @property

    def LastSavedTime(self)->'DateTime':
        """
        Gets or sets the date when a presentation was modified last time.
           
        """
        GetDllLibPpt().IDocumentProperty_get_LastSavedTime.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_LastSavedTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IDocumentProperty_get_LastSavedTime,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @LastSavedTime.setter
    def LastSavedTime(self, value:'DateTime'):
        GetDllLibPpt().IDocumentProperty_set_LastSavedTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_LastSavedTime,self.Ptr, value.Ptr)

    @property

    def LastPrinted(self)->'DateTime':
        """
        Gets or sets the date when a presentation was printed last time.

        """
        GetDllLibPpt().IDocumentProperty_get_LastPrinted.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_LastPrinted.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IDocumentProperty_get_LastPrinted,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @LastPrinted.setter
    def LastPrinted(self, value:'DateTime'):
        GetDllLibPpt().IDocumentProperty_set_LastPrinted.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_LastPrinted,self.Ptr, value.Ptr)

    @property

    def LastSavedBy(self)->str:
        """
        Gets or sets the name of a last person who modified a presentation.
           
        """
        GetDllLibPpt().IDocumentProperty_get_LastSavedBy.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_LastSavedBy.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_LastSavedBy,self.Ptr))
        return ret


    @LastSavedBy.setter
    def LastSavedBy(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_LastSavedBy.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_LastSavedBy,self.Ptr,valuePtr)

    @property
    def RevisionNumber(self)->int:
        """
        Gets or sets the presentation revision number.
           
        """
        GetDllLibPpt().IDocumentProperty_get_RevisionNumber.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_RevisionNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IDocumentProperty_get_RevisionNumber,self.Ptr)
        return ret

    @RevisionNumber.setter
    def RevisionNumber(self, value:int):
        GetDllLibPpt().IDocumentProperty_set_RevisionNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_RevisionNumber,self.Ptr, value)

    @property

    def ContentStatus(self)->str:
        """
        Gets or sets the content status of a presentation.
            
        """
        GetDllLibPpt().IDocumentProperty_get_ContentStatus.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_ContentStatus.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_ContentStatus,self.Ptr))
        return ret


    @ContentStatus.setter
    def ContentStatus(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_ContentStatus.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_ContentStatus,self.Ptr,valuePtr)

    @property

    def ContentType(self)->str:
        """
        Gets or sets the content type of a presentation.
            
        """
        GetDllLibPpt().IDocumentProperty_get_ContentType.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_ContentType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_ContentType,self.Ptr))
        return ret


    @ContentType.setter
    def ContentType(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_ContentType.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_ContentType,self.Ptr,valuePtr)

    @property
    def Count(self)->int:
        """
        Gets the number of custom properties actually contained in a collection.
            
        """
        GetDllLibPpt().IDocumentProperty_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IDocumentProperty_get_Count,self.Ptr)
        return ret

    @property

    def HyperlinkBase(self)->str:
        """
        Gets or sets the HyperlinkBase document property.
   
        """
        GetDllLibPpt().IDocumentProperty_get_HyperlinkBase.argtypes=[c_void_p]
        GetDllLibPpt().IDocumentProperty_get_HyperlinkBase.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_get_HyperlinkBase,self.Ptr))
        return ret


    @HyperlinkBase.setter
    def HyperlinkBase(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDocumentProperty_set_HyperlinkBase.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_HyperlinkBase,self.Ptr,valuePtr)


    def GetPropertyName(self ,index:int)->str:
        """
        Return a custom property name at the specified index.
        Args:
            index:The zero-based index of a custom property to get.
        returns:
            Custom property name at the specified index.
        """
        
        GetDllLibPpt().IDocumentProperty_GetPropertyName.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().IDocumentProperty_GetPropertyName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDocumentProperty_GetPropertyName,self.Ptr, index))
        return ret



    def Remove(self ,name:str)->bool:
        """
        Remove a custom property associated with a specified name.
        Args:
            name:Name of a custom property to remove.
        returns:
            Return true if a property was removed, false overwise.
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().IDocumentProperty_Remove.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().IDocumentProperty_Remove.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IDocumentProperty_Remove,self.Ptr,namePtr)
        return ret


    def Contains(self ,name:str)->bool:
        """
        Check presents of a custom property with a specified name.
        Args:
            name:Name of a custom property to check.
        returns:
            Return true if property exists, false overwise.
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().IDocumentProperty_Contains.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().IDocumentProperty_Contains.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IDocumentProperty_Contains,self.Ptr,namePtr)
        return ret


    def get_Item(self ,name:str)->'SpireObject':
        """
        Gets or sets the custom property associated with a specified name.
           
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().IDocumentProperty_get_Item.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().IDocumentProperty_get_Item.restype=IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().IDocumentProperty_get_Item,self.Ptr,namePtr)
        ret = None if intPtrWithTypeName==None else self._create(intPtrWithTypeName)
        return ret



    def set_Item(self ,name:str,value:'SpireObject'):
        """
        Set the custom property.
        Args:
            name:Name of a custom property.
            value:The value of custom property.
        """
        intPtrvalue:c_void_p = value.Ptr

        namePtr = StrToPtr(name)
        GetDllLibPpt().IDocumentProperty_set_Item.argtypes=[c_void_p ,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().IDocumentProperty_set_Item,self.Ptr,namePtr,intPtrvalue)

    @staticmethod
    def _create(intPtrWithTypeName:IntPtrWithTypeName)->'SpireObject':
        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'Boolean'):
            ret = Boolean(intPtr)
        elif (strName == 'Int32'):
            dlllib.Int32_Value.argtypes=[ c_void_p]
            dlllib.Int32_Value.restype=c_int
            intValue = CallCFunction(dlllib.Int32_Value, intPtr)
            ret = Int32(intValue)
        elif (strName == 'DateTime'):
            ret = DateTime(intPtr)
        else:
            ret = String(intPtr)
        return ret

