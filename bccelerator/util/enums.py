# -*- coding: bccelerator-transform-UTF-8 -*-

import enum as _enum
import typing as _typing

from . import polyfill as _polyfill


@_typing.final
@_enum.unique
class ContextMode(_polyfill.StrEnum):
    EDIT_MESH: _typing.ClassVar = 'EDIT_MESH'
    EDIT_CURVE: _typing.ClassVar = 'EDIT_CURVE'
    EDIT_CURVES: _typing.ClassVar = 'EDIT_CURVES'
    EDIT_SURFACE: _typing.ClassVar = 'EDIT_SURFACE'
    EDIT_TEXT: _typing.ClassVar = 'EDIT_TEXT'
    EDIT_ARMATURE: _typing.ClassVar = 'EDIT_ARMATURE'
    EDIT_METABALL: _typing.ClassVar = 'EDIT_METABALL'
    EDIT_LATTICE: _typing.ClassVar = 'EDIT_LATTICE'
    POSE: _typing.ClassVar = 'POSE'
    SCULPT: _typing.ClassVar = 'SCULPT'
    PAINT_WEIGHT: _typing.ClassVar = 'PAINT_WEIGHT'
    PAINT_VERTEX: _typing.ClassVar = 'PAINT_VERTEX'
    PAINT_TEXTURE: _typing.ClassVar = 'PAINT_TEXTURE'
    PARTICLE: _typing.ClassVar = 'PARTICLE'
    OBJECT: _typing.ClassVar = 'OBJECT'
    PAINT_GPENCIL: _typing.ClassVar = 'PAINT_GPENCIL'
    EDIT_GPENCIL: _typing.ClassVar = 'EDIT_GPENCIL'
    SCULPT_GPENCIL: _typing.ClassVar = 'SCULPT_GPENCIL'
    WEIGHT_GPENCIL: _typing.ClassVar = 'WEIGHT_GPENCIL'
    VERTEX_GPENCIL: _typing.ClassVar = 'VERTEX_GPENCIL'
    SCULPT_CURVES: _typing.ClassVar = 'SCULPT_CURVES'


@_typing.final
class Driver:
    @_typing.final
    @_enum.unique
    class Type(_polyfill.StrEnum):
        AVERAGE: _typing.ClassVar = 'AVERAGE'
        SUM: _typing.ClassVar = 'SUM'
        SCRIPTED: _typing.ClassVar = 'SCRIPTED'
        MIN: _typing.ClassVar = 'MIN'
        MAX: _typing.ClassVar = 'MAX'


@_typing.final
class DriverVariable:
    @_typing.final
    @_enum.unique
    class Type(_polyfill.StrEnum):
        SINGLE_PROP: _typing.ClassVar = 'SINGLE_PROP'
        TRANSFORMS: _typing.ClassVar = 'TRANSFORMS'
        ROTATION_DIFF: _typing.ClassVar = 'ROTATION_DIFF'
        LOC_DIFF: _typing.ClassVar = 'LOC_DIFF'


@_typing.final
@_enum.unique
class IDType(_polyfill.StrEnum):
    ACTION: _typing.ClassVar = 'ACTION'
    ARMATURE: _typing.ClassVar = 'ARMATURE'
    BRUSH: _typing.ClassVar = 'BRUSH'
    CACHEFILE: _typing.ClassVar = 'CACHEFILE'
    CAMERA: _typing.ClassVar = 'CAMERA'
    COLLECTION: _typing.ClassVar = 'COLLECTION'
    CURVE: _typing.ClassVar = 'CURVE'
    CURVES: _typing.ClassVar = 'CURVES'
    FONT: _typing.ClassVar = 'FONT'
    GREASEPENCIL: _typing.ClassVar = 'GREASEPENCIL'
    IMAGE: _typing.ClassVar = 'IMAGE'
    KEY: _typing.ClassVar = 'KEY'
    LATTICE: _typing.ClassVar = 'LATTICE'
    LIBRARY: _typing.ClassVar = 'LIBRARY'
    LIGHT: _typing.ClassVar = 'LIGHT'
    LIGHT_PROBE: _typing.ClassVar = 'LIGHT_PROBE'
    LINESTYLE: _typing.ClassVar = 'LINESTYLE'
    MASK: _typing.ClassVar = 'MASK'
    MATERIAL: _typing.ClassVar = 'MATERIAL'
    MESH: _typing.ClassVar = 'MESH'
    META: _typing.ClassVar = 'META'
    MOVIECLIP: _typing.ClassVar = 'MOVIECLIP'
    NODETREE: _typing.ClassVar = 'NODETREE'
    OBJECT: _typing.ClassVar = 'OBJECT'
    PAINTCURVE: _typing.ClassVar = 'PAINTCURVE'
    PALETTE: _typing.ClassVar = 'PALETTE'
    PARTICLE: _typing.ClassVar = 'PARTICLE'
    POINTCLOUD: _typing.ClassVar = 'POINTCLOUD'
    SCENE: _typing.ClassVar = 'SCENE'
    SIMULATION: _typing.ClassVar = 'SIMULATION'
    SOUND: _typing.ClassVar = 'SOUND'
    SPEAKER: _typing.ClassVar = 'SPEAKER'
    TEXT: _typing.ClassVar = 'TEXT'
    TEXTURE: _typing.ClassVar = 'TEXTURE'
    VOLUME: _typing.ClassVar = 'VOLUME'
    WINDOWMANAGER: _typing.ClassVar = 'WINDOWMANAGER'
    WORKSPACE: _typing.ClassVar = 'WORKSPACE'
    WORLD: _typing.ClassVar = 'WORLD'


@_typing.final
class Material:
    @_typing.final
    @_enum.unique
    class BlendMethod(_polyfill.StrEnum):
        OPAQUE: _typing.ClassVar = 'OPAQUE'
        CLIP: _typing.ClassVar = 'CLIP'
        HASHED: _typing.ClassVar = 'HASHED'
        BLEND: _typing.ClassVar = 'BLEND'

    @_typing.final
    @_enum.unique
    class ShadowMethod(_polyfill.StrEnum):
        NONE: _typing.ClassVar = 'NONE'
        OPAQUE: _typing.ClassVar = 'OPAQUE'
        CLIP: _typing.ClassVar = 'CLIP'
        HASHED: _typing.ClassVar = 'HASHED'


@_typing.final
class NLAStrip:
    @_typing.final
    @_enum.unique
    class Type(_polyfill.StrEnum):
        CLIP: _typing.ClassVar = 'CLIP'
        TRANSITION: _typing.ClassVar = 'TRANSITION'
        META: _typing.ClassVar = 'META'
        SOUND: _typing.ClassVar = 'SOUND'


@_typing.final
class Object:
    @_typing.final
    @_enum.unique
    class InstanceType(_polyfill.StrEnum):
        NONE: _typing.ClassVar = 'NONE'
        VERTS: _typing.ClassVar = 'VERTS'
        FACES: _typing.ClassVar = 'FACES'
        COLLECTION: _typing.ClassVar = 'COLLECTION'


@_typing.final
@_enum.unique
class ObjectModifierType(_polyfill.StrEnum):
    DATA_TRANSFER: _typing.ClassVar = 'DATA_TRANSFER'
    MESH_CACHE: _typing.ClassVar = 'MESH_CACHE'
    MESH_SEQUENCE_CACHE: _typing.ClassVar = 'MESH_SEQUENCE_CACHE'
    NORMAL_EDIT: _typing.ClassVar = 'NORMAL_EDIT'
    WEIGHTED_NORMAL: _typing.ClassVar = 'WEIGHTED_NORMAL'
    UV_PROJECT: _typing.ClassVar = 'UV_PROJECT'
    UV_WARP: _typing.ClassVar = 'UV_WARP'
    VERTEX_WEIGHT_EDIT: _typing.ClassVar = 'VERTEX_WEIGHT_EDIT'
    VERTEX_WEIGHT_MIX: _typing.ClassVar = 'VERTEX_WEIGHT_MIX'
    VERTEX_WEIGHT_PROXIMITY: _typing.ClassVar = 'VERTEX_WEIGHT_PROXIMITY'
    ARRAY: _typing.ClassVar = 'ARRAY'
    BEVEL: _typing.ClassVar = 'BEVEL'
    BOOLEAN: _typing.ClassVar = 'BOOLEAN'
    BUILD: _typing.ClassVar = 'BUILD'
    DECIMATE: _typing.ClassVar = 'DECIMATE'
    EDGE_SPLIT: _typing.ClassVar = 'EDGE_SPLIT'
    NODES: _typing.ClassVar = 'NODES'
    MASK: _typing.ClassVar = 'MASK'
    MIRROR: _typing.ClassVar = 'MIRROR'
    MESH_TO_VOLUME: _typing.ClassVar = 'MESH_TO_VOLUME'
    MULTIRES: _typing.ClassVar = 'MULTIRES'
    REMESH: _typing.ClassVar = 'REMESH'
    SCREW: _typing.ClassVar = 'SCREW'
    SKIN: _typing.ClassVar = 'SKIN'
    SOLIDIFY: _typing.ClassVar = 'SOLIDIFY'
    SUBSURF: _typing.ClassVar = 'SUBSURF'
    TRIANGULATE: _typing.ClassVar = 'TRIANGULATE'
    VOLUME_TO_MESH: _typing.ClassVar = 'VOLUME_TO_MESH'
    WELD: _typing.ClassVar = 'WELD'
    WIREFRAME: _typing.ClassVar = 'WIREFRAME'
    ARMATURE: _typing.ClassVar = 'ARMATURE'
    CAST: _typing.ClassVar = 'CAST'
    CURVE: _typing.ClassVar = 'CURVE'
    DISPLACE: _typing.ClassVar = 'DISPLACE'
    HOOK: _typing.ClassVar = 'HOOK'
    LAPLACIANDEFORM: _typing.ClassVar = 'LAPLACIANDEFORM'
    LATTICE: _typing.ClassVar = 'LATTICE'
    MESH_DEFORM: _typing.ClassVar = 'MESH_DEFORM'
    SHRINKWRAP: _typing.ClassVar = 'SHRINKWRAP'
    SIMPLE_DEFORM: _typing.ClassVar = 'SIMPLE_DEFORM'
    SMOOTH: _typing.ClassVar = 'SMOOTH'
    CORRECTIVE_SMOOTH: _typing.ClassVar = 'CORRECTIVE_SMOOTH'
    LAPLACIANSMOOTH: _typing.ClassVar = 'LAPLACIANSMOOTH'
    SURFACE_DEFORM: _typing.ClassVar = 'SURFACE_DEFORM'
    WARP: _typing.ClassVar = 'WARP'
    WAVE: _typing.ClassVar = 'WAVE'
    VOLUME_DISPLACE: _typing.ClassVar = 'VOLUME_DISPLACE'
    CLOTH: _typing.ClassVar = 'CLOTH'
    COLLISION: _typing.ClassVar = 'COLLISION'
    DYNAMIC_PAINT: _typing.ClassVar = 'DYNAMIC_PAINT'
    EXPLODE: _typing.ClassVar = 'EXPLODE'
    FLUID: _typing.ClassVar = 'FLUID'
    OCEAN: _typing.ClassVar = 'OCEAN'
    PARTICLE_INSTANCE: _typing.ClassVar = 'PARTICLE_INSTANCE'
    PARTICLE_SYSTEM: _typing.ClassVar = 'PARTICLE_SYSTEM'
    SOFT_BODY: _typing.ClassVar = 'SOFT_BODY'
    SURFACE: _typing.ClassVar = 'SURFACE'


@_typing.final
@_enum.unique
class OperatorReturn(_polyfill.StrEnum):
    RUNNING_MODAL: _typing.ClassVar = 'RUNNING_MODAL'
    CANCELLED: _typing.ClassVar = 'CANCELLED'
    FINISHED: _typing.ClassVar = 'FINISHED'
    PASS_THROUGH: _typing.ClassVar = 'PASS_THROUGH'
    INTERFACE: _typing.ClassVar = 'INTERFACE'


@_typing.final
@_enum.unique
class OperatorTypeFlag(_polyfill.StrEnum):
    REGISTER: _typing.ClassVar = 'REGISTER'
    UNDO: _typing.ClassVar = 'UNDO'
    UNDO_GROUPED: _typing.ClassVar = 'UNDO_GROUPED'
    BLOCKING: _typing.ClassVar = 'BLOCKING'
    MACRO: _typing.ClassVar = 'MACRO'
    GRAB_CURSOR: _typing.ClassVar = 'GRAB_CURSOR'
    GRAB_CURSOR_X: _typing.ClassVar = 'GRAB_CURSOR_X'
    GRAB_CURSOR_Y: _typing.ClassVar = 'GRAB_CURSOR_Y'
    DEPENDS_ON_CURSOR: _typing.ClassVar = 'DEPENDS_ON_CURSOR'
    PRESET: _typing.ClassVar = 'PRESET'
    INTERNAL: _typing.ClassVar = 'INTERNAL'


@_typing.final
@_enum.unique
class PropertyFlagEnum(_polyfill.StrEnum):
    HIDDEN: _typing.ClassVar = 'HIDDEN'
    SKIP_SAVE: _typing.ClassVar = 'SKIP_SAVE'
    ANIMATABLE: _typing.ClassVar = 'ANIMATABLE'
    LIBRARY_EDITABLE: _typing.ClassVar = 'LIBRARY_EDITABLE'
    ENUM_FLAG: _typing.ClassVar = 'ENUM_FLAG'


@_typing.final
@_enum.unique
class PropertySubtype(_polyfill.StrEnum):
    NONE: _typing.ClassVar = 'NONE'
    FILE_PATH: _typing.ClassVar = 'FILE_PATH'
    DIR_PATH: _typing.ClassVar = 'DIR_PATH'
    FILE_NAME: _typing.ClassVar = 'FILE_NAME'
    BYTE_STRING: _typing.ClassVar = 'BYTE_STRING'
    PASSWORD: _typing.ClassVar = 'PASSWORD'
    PIXEL: _typing.ClassVar = 'PIXEL'
    UNSIGNED: _typing.ClassVar = 'UNSIGNED'
    PERCENTAGE: _typing.ClassVar = 'PERCENTAGE'
    FACTOR: _typing.ClassVar = 'FACTOR'
    ANGLE: _typing.ClassVar = 'ANGLE'
    TIME: _typing.ClassVar = 'TIME'
    TIME_ABSOLUTE: _typing.ClassVar = 'TIME_ABSOLUTE'
    DISTANCE: _typing.ClassVar = 'DISTANCE'
    DISTANCE_CAMERA: _typing.ClassVar = 'DISTANCE_CAMERA'
    POWER: _typing.ClassVar = 'POWER'
    TEMPERATURE: _typing.ClassVar = 'TEMPERATURE'
    COLOR: _typing.ClassVar = 'COLOR'
    TRANSLATION: _typing.ClassVar = 'TRANSLATION'
    DIRECTION: _typing.ClassVar = 'DIRECTION'
    VELOCITY: _typing.ClassVar = 'VELOCITY'
    ACCELERATION: _typing.ClassVar = 'ACCELERATION'
    MATRIX: _typing.ClassVar = 'MATRIX'
    EULER: _typing.ClassVar = 'EULER'
    QUATERNION: _typing.ClassVar = 'QUATERNION'
    AXISANGLE: _typing.ClassVar = 'AXISANGLE'
    XYZ: _typing.ClassVar = 'XYZ'
    XYZ_LENGTH: _typing.ClassVar = 'XYZ_LENGTH'
    COLOR_GAMMA: _typing.ClassVar = 'COLOR_GAMMA'
    COORDINATES: _typing.ClassVar = 'COORDINATES'
    LAYER: _typing.ClassVar = 'LAYER'
    LAYER_MEMBER: _typing.ClassVar = 'LAYER_MEMBER'


@_typing.final
@_enum.unique
class SpaceType(_polyfill.StrEnum):
    EMPTY: _typing.ClassVar = 'EMPTY'
    VIEW_3D: _typing.ClassVar = 'VIEW_3D'
    IMAGE_EDITOR: _typing.ClassVar = 'IMAGE_EDITOR'
    NODE_EDITOR: _typing.ClassVar = 'NODE_EDITOR'
    SEQUENCE_EDITOR: _typing.ClassVar = 'SEQUENCE_EDITOR'
    CLIP_EDITOR: _typing.ClassVar = 'CLIP_EDITOR'
    DOPESHEET_EDITOR: _typing.ClassVar = 'DOPESHEET_EDITOR'
    GRAPH_EDITOR: _typing.ClassVar = 'GRAPH_EDITOR'
    NLA_EDITOR: _typing.ClassVar = 'NLA_EDITOR'
    TEXT_EDITOR: _typing.ClassVar = 'TEXT_EDITOR'
    CONSOLE: _typing.ClassVar = 'CONSOLE'
    INFO: _typing.ClassVar = 'INFO'
    TOPBAR: _typing.ClassVar = 'TOPBAR'
    STATUSBAR: _typing.ClassVar = 'STATUSBAR'
    OUTLINER: _typing.ClassVar = 'OUTLINER'
    PROPERTIES: _typing.ClassVar = 'PROPERTIES'
    FILE_BROWSER: _typing.ClassVar = 'FILE_BROWSER'
    SPREADSHEET: _typing.ClassVar = 'SPREADSHEET'
    PREFERENCES: _typing.ClassVar = 'PREFERENCES'


@_typing.final
@_enum.unique
class WMReport(_polyfill.StrEnum):
    DEBUG: _typing.ClassVar = 'DEBUG'
    INFO: _typing.ClassVar = 'INFO'
    OPERATOR: _typing.ClassVar = 'OPERATOR'
    PROPERTY: _typing.ClassVar = 'PROPERTY'
    WARNING: _typing.ClassVar = 'WARNING'
    ERROR: _typing.ClassVar = 'ERROR'
    ERROR_INVALID_INPUT: _typing.ClassVar = 'ERROR_INVALID_INPUT'
    ERROR_INVALID_CONTEXT: _typing.ClassVar = 'ERROR_INVALID_CONTEXT'
    ERROR_OUT_OF_MEMORY: _typing.ClassVar = 'ERROR_OUT_OF_MEMORY'
