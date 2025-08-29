from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextHighLightingOptions (SpireObject) :
    """
    Configuration options for text highlighting operations.
    
    Provides settings to control how text is searched and highlighted
    during text processing operations.
    """

    @dispatch
    def __init__(self):
        """
        Initialize a new instance with default highlighting options.
        
        Default options are case-insensitive and allow partial word matches.
        """
        GetDllLibPpt().TextHighLightingOptions_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextHighLightingOptions_Create)
        super(TextHighLightingOptions, self).__init__(intPtr)
    """

    """
    @property
    def CaseSensitive(self)->bool:
        """
        Enable or disable case-sensitive text search.
        
        When set to True, searches will distinguish between uppercase and lowercase letters.
        When False (default), searches will ignore case differences.
        
        Returns:
            bool: Current case-sensitivity setting
        """
        GetDllLibPpt().TextHighLightingOptions_get_CaseSensitive.argtypes=[c_void_p]
        GetDllLibPpt().TextHighLightingOptions_get_CaseSensitive.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextHighLightingOptions_get_CaseSensitive,self.Ptr)
        return ret

    @CaseSensitive.setter
    def CaseSensitive(self, value:bool):
        """
        Configure case-sensitivity for text search operations.
        
        Args:
            value: True for case-sensitive search, False for case-insensitive
        """
        GetDllLibPpt().TextHighLightingOptions_set_CaseSensitive.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextHighLightingOptions_set_CaseSensitive,self.Ptr, value)

    @property
    def WholeWordsOnly(self)->bool:
        """
        Require whole-word matching for text search.
        
        When set to True, searches will only match complete words.
        When False (default), searches will match partial words within text.
        
        Returns:
            bool: Current whole-word matching setting
        """
        GetDllLibPpt().TextHighLightingOptions_get_WholeWordsOnly.argtypes=[c_void_p]
        GetDllLibPpt().TextHighLightingOptions_get_WholeWordsOnly.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextHighLightingOptions_get_WholeWordsOnly,self.Ptr)
        return ret

    @WholeWordsOnly.setter
    def WholeWordsOnly(self, value:bool):
        """
        Configure whole-word matching requirement.
        
        Args:
            value: True to require whole-word matches, False to allow partial matches
        """
        GetDllLibPpt().TextHighLightingOptions_set_WholeWordsOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextHighLightingOptions_set_WholeWordsOnly,self.Ptr, value)

