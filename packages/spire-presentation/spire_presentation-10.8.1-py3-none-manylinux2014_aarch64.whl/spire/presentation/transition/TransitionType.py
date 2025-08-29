from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionType(Enum):
    """
    Specifies slide show transition effects.
    
    Attributes:
        none: No transition effect.
        Airplane: Airplane transition effect.
        Blinds: Blinds transition effect.
        Box: Box transition effect.
        Checker: Checker transition effect.
        Circle: Circle transition effect.
        Comb: Comb transition effect.
        Conveyor: Conveyor transition effect.
        Cover: Cover transition effect.
        Cut: Cut transition effect.
        Cube: Cube transition effect.
        Curtains: Curtains transition effect.
        Crush: Crush transition effect.
        Diamond: Diamond transition effect.
        Dissolve: Dissolve transition effect.
        Doors: Doors transition effect.
        Drape: Drape transition effect.
        Fade: Fade transition effect.
        Ferris: Ferris wheel transition effect.
        FLash: Flash transition effect.
        Flip: Flip transition effect.
        Flythrough: Flythrough transition effect.
        Fracture: Fracture transition effect.
        FallOver: Fall over transition effect.
        Gallery: Gallery transition effect.
        Glitter: Glitter transition effect.
        Honeycomb: Honeycomb transition effect.
        Newsflash: Newsflash transition effect.
        Orbit: Orbit transition effect.
        Origami: Origami transition effect.
        PageCurlDouble: Double page curl transition effect.
        Pan: Pan transition effect.
        PeelOff: Peel off transition effect.
        Plus: Plus transition effect.
        Prestige: Prestige transition effect.
        Pull: Pull transition effect.
        Push: Push transition effect.
        Random: Random transition effect.
        Reveal: Reveal transition effect.
        RandomBar: Random bar transition effect.
        Ripple: Ripple transition effect.
        Rotate: Rotate transition effect.
        Shred: Shred transition effect.
        SoundAction: Sound action transition effect.
        Split: Split transition effect.
        Strips: Strips transition effect.
        Switch: Switch transition effect.
        Vortex: Vortex transition effect.
        Wedge: Wedge transition effect.
        Wheel: Wheel transition effect.
        Wipe: Wipe transition effect.
        Window: Window transition effect.
        Wind: Wind transition effect.
        Warp: Warp transition effect.
        Zoom: Zoom transition effect.
        Morph: Morph transition effect.
    """
    none = 0
    Airplane = 1
    Blinds = 2
    Box = 3
    Checker = 4
    Circle = 5
    Comb = 6
    Conveyor = 7
    Cover = 8
    Cut = 9
    Cube = 10
    Curtains = 11
    Crush = 12
    Diamond = 13
    Dissolve = 14
    Doors = 15
    Drape = 16
    Fade = 17
    Ferris = 18
    FLash = 19
    Flip = 20
    Flythrough = 21
    Fracture = 22
    FallOver = 23
    Gallery = 24
    Glitter = 25
    Honeycomb = 26
    Newsflash = 27
    Orbit = 28
    Origami = 29
    PageCurlDouble = 30
    Pan = 31
    PeelOff = 32
    Plus = 33
    Prestige = 34
    Pull = 35
    Push = 36
    Random = 37
    Reveal = 38
    RandomBar = 39
    Ripple = 40
    Rotate = 41
    Shred = 42
    SoundAction = 43
    Split = 44
    Strips = 45
    Switch = 46
    Vortex = 47
    Wedge = 48
    Wheel = 49
    Wipe = 50
    Window = 51
    Wind = 52
    Warp = 53
    Zoom = 54
    Morph = 55

