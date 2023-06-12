# -*- coding: bccelerator-transform-UTF-8 -*-
from enum import unique as _unique
from typing import ClassVar as _ClassVar, final as _final

from .polyfill import StrEnum as _StrEnum


@_final
@_unique
class ContextMode(_StrEnum):
    __slots__: _ClassVar = ()

    EDIT_MESH: _ClassVar = "EDIT_MESH"
    EDIT_CURVE: _ClassVar = "EDIT_CURVE"
    EDIT_CURVES: _ClassVar = "EDIT_CURVES"
    EDIT_SURFACE: _ClassVar = "EDIT_SURFACE"
    EDIT_TEXT: _ClassVar = "EDIT_TEXT"
    EDIT_ARMATURE: _ClassVar = "EDIT_ARMATURE"
    EDIT_METABALL: _ClassVar = "EDIT_METABALL"
    EDIT_LATTICE: _ClassVar = "EDIT_LATTICE"
    POSE: _ClassVar = "POSE"
    SCULPT: _ClassVar = "SCULPT"
    PAINT_WEIGHT: _ClassVar = "PAINT_WEIGHT"
    PAINT_VERTEX: _ClassVar = "PAINT_VERTEX"
    PAINT_TEXTURE: _ClassVar = "PAINT_TEXTURE"
    PARTICLE: _ClassVar = "PARTICLE"
    OBJECT: _ClassVar = "OBJECT"
    PAINT_GPENCIL: _ClassVar = "PAINT_GPENCIL"
    EDIT_GPENCIL: _ClassVar = "EDIT_GPENCIL"
    SCULPT_GPENCIL: _ClassVar = "SCULPT_GPENCIL"
    WEIGHT_GPENCIL: _ClassVar = "WEIGHT_GPENCIL"
    VERTEX_GPENCIL: _ClassVar = "VERTEX_GPENCIL"
    SCULPT_CURVES: _ClassVar = "SCULPT_CURVES"


@_final
class Driver:
    __slots__: _ClassVar = ()

    @_final
    @_unique
    class Type(_StrEnum):
        __slots__: _ClassVar = ()

        AVERAGE: _ClassVar = "AVERAGE"
        SUM: _ClassVar = "SUM"
        SCRIPTED: _ClassVar = "SCRIPTED"
        MIN: _ClassVar = "MIN"
        MAX: _ClassVar = "MAX"


@_final
class DriverVariable:
    __slots__: _ClassVar = ()

    @_final
    @_unique
    class Type(_StrEnum):
        __slots__: _ClassVar = ()

        SINGLE_PROP: _ClassVar = "SINGLE_PROP"
        TRANSFORMS: _ClassVar = "TRANSFORMS"
        ROTATION_DIFF: _ClassVar = "ROTATION_DIFF"
        LOC_DIFF: _ClassVar = "LOC_DIFF"


@_final
@_unique
class FModifierType(_StrEnum):
    __slots__: _ClassVar = ()

    CYCLES: _ClassVar = "CYCLES"
    ENVELOPE: _ClassVar = "ENVELOPE"
    FNGENERATOR: _ClassVar = "FNGENERATOR"
    GENERATOR: _ClassVar = "GENERATOR"
    LIMITS: _ClassVar = "LIMITS"
    NOISE: _ClassVar = "NOISE"
    NULL: _ClassVar = "NULL"
    STEPPED: _ClassVar = "STEPPED"


@_final
@_unique
class IDType(_StrEnum):
    __slots__: _ClassVar = ()

    ACTION: _ClassVar = "ACTION"
    ARMATURE: _ClassVar = "ARMATURE"
    BRUSH: _ClassVar = "BRUSH"
    CACHEFILE: _ClassVar = "CACHEFILE"
    CAMERA: _ClassVar = "CAMERA"
    COLLECTION: _ClassVar = "COLLECTION"
    CURVE: _ClassVar = "CURVE"
    CURVES: _ClassVar = "CURVES"
    FONT: _ClassVar = "FONT"
    GREASEPENCIL: _ClassVar = "GREASEPENCIL"
    IMAGE: _ClassVar = "IMAGE"
    KEY: _ClassVar = "KEY"
    LATTICE: _ClassVar = "LATTICE"
    LIBRARY: _ClassVar = "LIBRARY"
    LIGHT: _ClassVar = "LIGHT"
    LIGHT_PROBE: _ClassVar = "LIGHT_PROBE"
    LINESTYLE: _ClassVar = "LINESTYLE"
    MASK: _ClassVar = "MASK"
    MATERIAL: _ClassVar = "MATERIAL"
    MESH: _ClassVar = "MESH"
    META: _ClassVar = "META"
    MOVIECLIP: _ClassVar = "MOVIECLIP"
    NODETREE: _ClassVar = "NODETREE"
    OBJECT: _ClassVar = "OBJECT"
    PAINTCURVE: _ClassVar = "PAINTCURVE"
    PALETTE: _ClassVar = "PALETTE"
    PARTICLE: _ClassVar = "PARTICLE"
    POINTCLOUD: _ClassVar = "POINTCLOUD"
    SCENE: _ClassVar = "SCENE"
    SIMULATION: _ClassVar = "SIMULATION"
    SOUND: _ClassVar = "SOUND"
    SPEAKER: _ClassVar = "SPEAKER"
    TEXT: _ClassVar = "TEXT"
    TEXTURE: _ClassVar = "TEXTURE"
    VOLUME: _ClassVar = "VOLUME"
    WINDOWMANAGER: _ClassVar = "WINDOWMANAGER"
    WORKSPACE: _ClassVar = "WORKSPACE"
    WORLD: _ClassVar = "WORLD"


@_final
class Material:
    __slots__: _ClassVar = ()

    @_final
    @_unique
    class BlendMethod(_StrEnum):
        __slots__: _ClassVar = ()

        OPAQUE: _ClassVar = "OPAQUE"
        CLIP: _ClassVar = "CLIP"
        HASHED: _ClassVar = "HASHED"
        BLEND: _ClassVar = "BLEND"

    @_final
    @_unique
    class ShadowMethod(_StrEnum):
        __slots__: _ClassVar = ()

        NONE: _ClassVar = "NONE"
        OPAQUE: _ClassVar = "OPAQUE"
        CLIP: _ClassVar = "CLIP"
        HASHED: _ClassVar = "HASHED"


@_final
class NLAStrip:
    __slots__: _ClassVar = ()

    @_final
    @_unique
    class Type(_StrEnum):
        __slots__: _ClassVar = ()

        CLIP: _ClassVar = "CLIP"
        TRANSITION: _ClassVar = "TRANSITION"
        META: _ClassVar = "META"
        SOUND: _ClassVar = "SOUND"


@_final
class Object:
    __slots__: _ClassVar = ()

    @_final
    @_unique
    class InstanceType(_StrEnum):
        __slots__: _ClassVar = ()

        NONE: _ClassVar = "NONE"
        VERTS: _ClassVar = "VERTS"
        FACES: _ClassVar = "FACES"
        COLLECTION: _ClassVar = "COLLECTION"


@_final
@_unique
class ObjectModifierType(_StrEnum):
    __slots__: _ClassVar = ()

    DATA_TRANSFER: _ClassVar = "DATA_TRANSFER"
    MESH_CACHE: _ClassVar = "MESH_CACHE"
    MESH_SEQUENCE_CACHE: _ClassVar = "MESH_SEQUENCE_CACHE"
    NORMAL_EDIT: _ClassVar = "NORMAL_EDIT"
    WEIGHTED_NORMAL: _ClassVar = "WEIGHTED_NORMAL"
    UV_PROJECT: _ClassVar = "UV_PROJECT"
    UV_WARP: _ClassVar = "UV_WARP"
    VERTEX_WEIGHT_EDIT: _ClassVar = "VERTEX_WEIGHT_EDIT"
    VERTEX_WEIGHT_MIX: _ClassVar = "VERTEX_WEIGHT_MIX"
    VERTEX_WEIGHT_PROXIMITY: _ClassVar = "VERTEX_WEIGHT_PROXIMITY"
    ARRAY: _ClassVar = "ARRAY"
    BEVEL: _ClassVar = "BEVEL"
    BOOLEAN: _ClassVar = "BOOLEAN"
    BUILD: _ClassVar = "BUILD"
    DECIMATE: _ClassVar = "DECIMATE"
    EDGE_SPLIT: _ClassVar = "EDGE_SPLIT"
    NODES: _ClassVar = "NODES"
    MASK: _ClassVar = "MASK"
    MIRROR: _ClassVar = "MIRROR"
    MESH_TO_VOLUME: _ClassVar = "MESH_TO_VOLUME"
    MULTIRES: _ClassVar = "MULTIRES"
    REMESH: _ClassVar = "REMESH"
    SCREW: _ClassVar = "SCREW"
    SKIN: _ClassVar = "SKIN"
    SOLIDIFY: _ClassVar = "SOLIDIFY"
    SUBSURF: _ClassVar = "SUBSURF"
    TRIANGULATE: _ClassVar = "TRIANGULATE"
    VOLUME_TO_MESH: _ClassVar = "VOLUME_TO_MESH"
    WELD: _ClassVar = "WELD"
    WIREFRAME: _ClassVar = "WIREFRAME"
    ARMATURE: _ClassVar = "ARMATURE"
    CAST: _ClassVar = "CAST"
    CURVE: _ClassVar = "CURVE"
    DISPLACE: _ClassVar = "DISPLACE"
    HOOK: _ClassVar = "HOOK"
    LAPLACIANDEFORM: _ClassVar = "LAPLACIANDEFORM"
    LATTICE: _ClassVar = "LATTICE"
    MESH_DEFORM: _ClassVar = "MESH_DEFORM"
    SHRINKWRAP: _ClassVar = "SHRINKWRAP"
    SIMPLE_DEFORM: _ClassVar = "SIMPLE_DEFORM"
    SMOOTH: _ClassVar = "SMOOTH"
    CORRECTIVE_SMOOTH: _ClassVar = "CORRECTIVE_SMOOTH"
    LAPLACIANSMOOTH: _ClassVar = "LAPLACIANSMOOTH"
    SURFACE_DEFORM: _ClassVar = "SURFACE_DEFORM"
    WARP: _ClassVar = "WARP"
    WAVE: _ClassVar = "WAVE"
    VOLUME_DISPLACE: _ClassVar = "VOLUME_DISPLACE"
    CLOTH: _ClassVar = "CLOTH"
    COLLISION: _ClassVar = "COLLISION"
    DYNAMIC_PAINT: _ClassVar = "DYNAMIC_PAINT"
    EXPLODE: _ClassVar = "EXPLODE"
    FLUID: _ClassVar = "FLUID"
    OCEAN: _ClassVar = "OCEAN"
    PARTICLE_INSTANCE: _ClassVar = "PARTICLE_INSTANCE"
    PARTICLE_SYSTEM: _ClassVar = "PARTICLE_SYSTEM"
    SOFT_BODY: _ClassVar = "SOFT_BODY"
    SURFACE: _ClassVar = "SURFACE"


@_final
@_unique
class OperatorReturn(_StrEnum):
    __slots__: _ClassVar = ()

    RUNNING_MODAL: _ClassVar = "RUNNING_MODAL"
    CANCELLED: _ClassVar = "CANCELLED"
    FINISHED: _ClassVar = "FINISHED"
    PASS_THROUGH: _ClassVar = "PASS_THROUGH"
    INTERFACE: _ClassVar = "INTERFACE"


@_final
@_unique
class OperatorTypeFlag(_StrEnum):
    __slots__: _ClassVar = ()

    REGISTER: _ClassVar = "REGISTER"
    UNDO: _ClassVar = "UNDO"
    UNDO_GROUPED: _ClassVar = "UNDO_GROUPED"
    BLOCKING: _ClassVar = "BLOCKING"
    MACRO: _ClassVar = "MACRO"
    GRAB_CURSOR: _ClassVar = "GRAB_CURSOR"
    GRAB_CURSOR_X: _ClassVar = "GRAB_CURSOR_X"
    GRAB_CURSOR_Y: _ClassVar = "GRAB_CURSOR_Y"
    DEPENDS_ON_CURSOR: _ClassVar = "DEPENDS_ON_CURSOR"
    PRESET: _ClassVar = "PRESET"
    INTERNAL: _ClassVar = "INTERNAL"


@_final
@_unique
class PropertyFlagEnum(_StrEnum):
    __slots__: _ClassVar = ()

    HIDDEN: _ClassVar = "HIDDEN"
    SKIP_SAVE: _ClassVar = "SKIP_SAVE"
    ANIMATABLE: _ClassVar = "ANIMATABLE"
    LIBRARY_EDITABLE: _ClassVar = "LIBRARY_EDITABLE"
    ENUM_FLAG: _ClassVar = "ENUM_FLAG"


@_final
@_unique
class PropertySubtype(_StrEnum):
    __slots__: _ClassVar = ()

    NONE: _ClassVar = "NONE"
    FILE_PATH: _ClassVar = "FILE_PATH"
    DIR_PATH: _ClassVar = "DIR_PATH"
    FILE_NAME: _ClassVar = "FILE_NAME"
    BYTE_STRING: _ClassVar = "BYTE_STRING"
    PASSWORD: _ClassVar = "PASSWORD"
    PIXEL: _ClassVar = "PIXEL"
    UNSIGNED: _ClassVar = "UNSIGNED"
    PERCENTAGE: _ClassVar = "PERCENTAGE"
    FACTOR: _ClassVar = "FACTOR"
    ANGLE: _ClassVar = "ANGLE"
    TIME: _ClassVar = "TIME"
    TIME_ABSOLUTE: _ClassVar = "TIME_ABSOLUTE"
    DISTANCE: _ClassVar = "DISTANCE"
    DISTANCE_CAMERA: _ClassVar = "DISTANCE_CAMERA"
    POWER: _ClassVar = "POWER"
    TEMPERATURE: _ClassVar = "TEMPERATURE"
    COLOR: _ClassVar = "COLOR"
    TRANSLATION: _ClassVar = "TRANSLATION"
    DIRECTION: _ClassVar = "DIRECTION"
    VELOCITY: _ClassVar = "VELOCITY"
    ACCELERATION: _ClassVar = "ACCELERATION"
    MATRIX: _ClassVar = "MATRIX"
    EULER: _ClassVar = "EULER"
    QUATERNION: _ClassVar = "QUATERNION"
    AXISANGLE: _ClassVar = "AXISANGLE"
    XYZ: _ClassVar = "XYZ"
    XYZ_LENGTH: _ClassVar = "XYZ_LENGTH"
    COLOR_GAMMA: _ClassVar = "COLOR_GAMMA"
    COORDINATES: _ClassVar = "COORDINATES"
    LAYER: _ClassVar = "LAYER"
    LAYER_MEMBER: _ClassVar = "LAYER_MEMBER"


@_final
@_unique
class SpaceType(_StrEnum):
    __slots__: _ClassVar = ()

    EMPTY: _ClassVar = "EMPTY"
    VIEW_3D: _ClassVar = "VIEW_3D"
    IMAGE_EDITOR: _ClassVar = "IMAGE_EDITOR"
    NODE_EDITOR: _ClassVar = "NODE_EDITOR"
    SEQUENCE_EDITOR: _ClassVar = "SEQUENCE_EDITOR"
    CLIP_EDITOR: _ClassVar = "CLIP_EDITOR"
    DOPESHEET_EDITOR: _ClassVar = "DOPESHEET_EDITOR"
    GRAPH_EDITOR: _ClassVar = "GRAPH_EDITOR"
    NLA_EDITOR: _ClassVar = "NLA_EDITOR"
    TEXT_EDITOR: _ClassVar = "TEXT_EDITOR"
    CONSOLE: _ClassVar = "CONSOLE"
    INFO: _ClassVar = "INFO"
    TOPBAR: _ClassVar = "TOPBAR"
    STATUSBAR: _ClassVar = "STATUSBAR"
    OUTLINER: _ClassVar = "OUTLINER"
    PROPERTIES: _ClassVar = "PROPERTIES"
    FILE_BROWSER: _ClassVar = "FILE_BROWSER"
    SPREADSHEET: _ClassVar = "SPREADSHEET"
    PREFERENCES: _ClassVar = "PREFERENCES"


@_final
@_unique
class WMReport(_StrEnum):
    __slots__: _ClassVar = ()

    DEBUG: _ClassVar = "DEBUG"
    INFO: _ClassVar = "INFO"
    OPERATOR: _ClassVar = "OPERATOR"
    PROPERTY: _ClassVar = "PROPERTY"
    WARNING: _ClassVar = "WARNING"
    ERROR: _ClassVar = "ERROR"
    ERROR_INVALID_INPUT: _ClassVar = "ERROR_INVALID_INPUT"
    ERROR_INVALID_CONTEXT: _ClassVar = "ERROR_INVALID_CONTEXT"
    ERROR_OUT_OF_MEMORY: _ClassVar = "ERROR_OUT_OF_MEMORY"
