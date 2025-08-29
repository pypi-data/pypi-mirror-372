from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineText (SpireObject) :

    @property

    def Ascent(self)->'float':
        """
    <summary>
        
    </summary>
        """
        GetDllLibPpt().LineText_get_Ascent.argtypes=[c_void_p]
        GetDllLibPpt().LineText_get_Ascent.restype=c_float
        ret = CallCFunction(GetDllLibPpt().LineText_get_Ascent,self.Ptr)
        return ret
    
    @property

    def Descent(self)->'float':
        """
    <summary>
        
    </summary>
        """
        GetDllLibPpt().LineText_get_Descent.argtypes=[c_void_p]
        GetDllLibPpt().LineText_get_Descent.restype=c_float
        ret = CallCFunction(GetDllLibPpt().LineText_get_Descent,self.Ptr)
        return ret
    
    @property

    def Text(self)->'str':
        """
    <summary>
        
    </summary>
        """
        GetDllLibPpt().LineText_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().LineText_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().LineText_get_Text,self.Ptr))
        return ret