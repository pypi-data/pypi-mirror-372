from enum import Enum
from plum import dispatch, dispatcher
from functools import singledispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LicenseProvider (SpireObject) :
    """
    Class Spire.Presentation.License.LicenseProvider.

    """
    @singledispatch
    @staticmethod
    def SetLicense(licenseFile):
        """
        Provides a license by a license file path or file stream, which will be used for loading license.

        Args:
            licenseFile:The full path of the license file or stream of the license file.
        """
        raise TypeError("Unsupport Type")


    @SetLicense.register
    def _SetLicense(licenseFile:str):
        """
        Provides a license by a license file path, which will be used for loading license.

        Args:
            licenseFile:The full path of the license file.
        """
        valuePtr = StrToPtr(licenseFile)
        GetDllLibPpt().LicenseProvider_SetLicenseFileFullPath.argtypes=[c_char_p]
        CallCFunction(GetDllLibPpt().LicenseProvider_SetLicenseFileFullPath,valuePtr)

    @SetLicense.register
    def _SetLicense(licenseFile:Stream):
        """
        Provides a license by a license stream, which will be used for loading license.

        Args:
            licenseFile:License data stream.
        """
        intPtrstream:c_void_p = licenseFile.Ptr
        GetDllLibPpt().LicenseProvider_SetLicenseFileStream.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().LicenseProvider_SetLicenseFileStream,intPtrstream)

    @staticmethod
    def SetLicenseKey(key:str,useDevOrTestLicense = None):
        """
    	Provides a license by a license key, which will be used for loading license.

		Args:
		    key:The value of the Key attribute of the element License of you license xml file.
            useDevOrTestLicense:Indicates whether to apply a development or test license.
        """
        keyPtr = StrToPtr(key)
        if(useDevOrTestLicense == None):
            GetDllLibPpt().LicenseProvider_SetLicenseKey.argtypes=[c_void_p]
            CallCFunction(GetDllLibPpt().LicenseProvider_SetLicenseKey,keyPtr)
        else:
            GetDllLibPpt().LicenseProvider_SetLicenseKey_useDevOrTestLicense.argtypes=[c_char_p,c_bool]
            CallCFunction(GetDllLibPpt().LicenseProvider_SetLicenseKey_useDevOrTestLicense,keyPtr,useDevOrTestLicense)

    @staticmethod
    def SetLicenseFileName(licenseFileName:str):
        """
        Sets the license file name, which will be used for loading license

        Args:
            licenseFileName:License file name.
        """
        valuePtr = StrToPtr(licenseFileName)
        GetDllLibPpt().LicenseProvider_SetLicenseFileName.argtypes=[c_char_p]
        CallCFunction(GetDllLibPpt().LicenseProvider_SetLicenseFileName,valuePtr)


    @staticmethod
    def ClearLicense():
        """
        Clear all cached license.

        """
        CallCFunction(GetDllLibPpt().LicenseProvider_ClearLicense)


    @staticmethod
    def LoadLicense():
        """
        Load the license provided by current setting to the license cache.

        """
        CallCFunction(GetDllLibPpt().LicenseProvider_LoadLicense)


    @staticmethod
    def UnbindDevelopmentOrTestingLicenses()->bool:
        """
        Unbound development or test license.
        
        returns:
            bool:true if a development or test license was found and successfully unbound; otherwise,false.

        """
        GetDllLibPpt().LicenseProvider_UnbindDevelopmentOrTestingLicenses.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LicenseProvider_UnbindDevelopmentOrTestingLicenses)
        return ret

    
