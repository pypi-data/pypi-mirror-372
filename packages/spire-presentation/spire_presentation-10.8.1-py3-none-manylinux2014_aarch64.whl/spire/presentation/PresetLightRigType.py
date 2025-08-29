from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetLightRigType(Enum):
    """
    Enumerates predefined lighting configurations for 3D object rendering.
    
    Attributes:
        none: No preset lighting applied.
        Balanced: Evenly distributed lighting.
        BrightRoom: Bright room-like illumination.
        Chilly: Cool-toned lighting effect.
        Contrasting: High-contrast lighting setup.
        Flat: Uniform, shadowless lighting.
        Flood: Intense floodlight illumination.
        Freezing: Extreme cool-toned lighting.
        Glow: Soft glowing light effect.
        Harsh: Strong directional lighting with sharp shadows.
        LegacyFlat1: Legacy flat lighting preset 1.
        # ... (other legacy presets)
        Morning: Simulated morning light conditions.
        Soft: Soft diffused lighting.
        Sunrise: Warm sunrise-like lighting.
        Sunset: Warm sunset-like lighting.
        ThreePt: Standard three-point lighting setup.
        TwoPt: Two-point lighting configuration.
    """
    none = -1
    Balanced = 0
    BrightRoom = 1
    Chilly = 2
    Contrasting = 3
    Flat = 4
    Flood = 5
    Freezing = 6
    Glow = 7
    Harsh = 8
    LegacyFlat1 = 9
    LegacyFlat2 = 10
    LegacyFlat3 = 11
    LegacyFlat4 = 12
    LegacyHarsh1 = 13
    LegacyHarsh2 = 14
    LegacyHarsh3 = 15
    LegacyHarsh4 = 16
    LegacyNormal1 = 17
    LegacyNormal2 = 18
    LegacyNormal3 = 19
    LegacyNormal4 = 20
    Morning = 21
    Soft = 22
    Sunrise = 23
    Sunset = 24
    ThreePt = 25
    TwoPt = 26

