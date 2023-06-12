# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy.ops import nla as _nla
from bpy.props import (
    EnumProperty as _EnumProp,  # type: ignore
    FloatProperty as _FloatProp,  # type: ignore
    IntProperty as _IntProp,  # type: ignore
)
from bpy.types import (
    Context as _Ctx,
    Event as _Evt,
    FModifierStepped as _FModStepped,
    ID as _ID,
    NlaStrip as _NlaStrip,
    NlaTrack as _NlaTrack,
    Object as _Obj,
    Operator as _Op,
)
from random import randint as _randint
from typing import Annotated as _Annotated, ClassVar as _ClassVar, cast as _cast

from ..utils import copy_attrs as _copy_attrs
from ..utils.enums import (
    FModifierType as _FModType,
    NLAStrip as _ENLAStrip,
    OperatorReturn as _OpReturn,
    OperatorTypeFlag as _OpTypeFlag,
    PropertyFlagEnum as _PropFlag,
    WMReport as _WMReport,
)
from ..utils.props import enum_property_item as _enum_prop_item
from ..utils.types import (
    Drawer as _Drawer,
    draw_func_class as _draw_func_class,
    internal_operator as _int_op,
)
from ..utils.utils import (
    ensure_animation_data as _ensure_anim_d,
    register_classes_factory as _reg_cls_fac,
)

_NLA_FMODIFIER_ADD = _nla.fmodifier_add  # type: ignore
_NLA_SELECT_ALL = _nla.select_all  # type: ignore
_NLA_SOUNDCLIP_ADD = _nla.soundclip_add  # type: ignore
_NLA_TRANSITION_ADD = _nla.transition_add  # type: ignore


def _copy_nla_strip(to_strip: _NlaStrip, from_strip: _NlaStrip):
    _copy_attrs(
        to_strip,
        (
            "action",
            "action_frame_end",
            "action_frame_start",
            # 'active',
            "blend_in",
            "blend_out",
            "blend_type",
            "extrapolation",
            # 'fcurves',
            "frame_end",
            # 'frame_end_ui',
            "frame_start",
            # 'frame_start_ui',
            "influence",
            # 'modifiers',
            "mute",
            "name",
            "repeat",
            "scale",
            # 'select',
            "strip_time",
            # 'strips',
            # 'type',
            "use_animated_influence",
            "use_animated_time",
            "use_animated_time_cyclic",
            "use_auto_blend",
            "use_reverse",
            "use_sync_length",
        ),
        from_strip,
    )


def _copy_nla_track(to_track: _NlaTrack, from_track: _NlaTrack):
    _copy_attrs(
        to_track,
        (
            # 'active',
            # 'is_override_data',
            # 'is_solo',
            "lock",
            "mute",
            "name",
            # 'select',
            # 'strips',
        ),
        from_track,
    )


class CopySelectedNLATrack(_Op):
    """Copy selected NLA track(s) to selected object(s)"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "nla.copy_selected_track"
    bl_label: _ClassVar = "Copy Selected NLA Track(s)"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        nla_track = context.active_nla_track
        return nla_track and any(
            obj is not _cast(_Obj, nla_track.id_data)
            for obj in context.selected_objects
        )

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        processed = 0
        from_track = context.active_nla_track
        for obj in context.selected_objects:
            if obj is not _cast(_Obj, from_track.id_data):
                to_track = _ensure_anim_d(obj).nla_tracks.new()
                _copy_nla_track(to_track, from_track)

                current_frame = context.scene.frame_current
                lock = to_track.lock
                try:
                    to_track.lock = False

                    transitions = list[int]()
                    for index, strip in enumerate(from_track.strips):
                        if strip.type == _ENLAStrip.Type.TRANSITION:
                            transitions.append(index)
                        elif strip.type == _ENLAStrip.Type.CLIP:
                            _copy_nla_strip(
                                to_track.strips.new(
                                    strip.name, int(strip.frame_start), strip.action
                                ),
                                strip,
                            )
                        elif strip.type == _ENLAStrip.Type.SOUND:
                            context.scene.frame_current = int(strip.frame_start)
                            _NLA_SOUNDCLIP_ADD()
                            new_strip = to_track.strips[-1]
                            _copy_nla_strip(new_strip, strip)
                        else:
                            self.report(
                                {_WMReport.WARNING},
                                f'Unsupported NLA strip "{strip.name}"',
                            )
                    for transition in transitions:
                        trans_from = to_track.strips[transition - 1]
                        trans_to = to_track.strips[transition]
                        _NLA_SELECT_ALL(action="DESELECT")
                        trans_from.select = trans_to.select = True
                        _NLA_TRANSITION_ADD()
                        trans_from.select = trans_to.select = False
                finally:
                    to_track.lock = lock
                    context.scene.frame_current = current_frame

                processed += 1
                self.report({_WMReport.INFO}, f'Copied to object "{obj.name_full}"')
        self.report({_WMReport.INFO}, f"Copied to {processed} object(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class RandomizeSelectedNLAStrip(_Op):
    """Randomize time of selected NLA strip(s), preserving order"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "nla.randomize_selected_strip"
    bl_label: _ClassVar = "Randomize Selected NLA Strip(s)"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return bool(context.selected_nla_strips)

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        processed = 0
        for nla_strip in context.selected_nla_strips:
            nla_tracks = (
                track
                for track in _ensure_anim_d(_cast(_ID, nla_strip.id_data)).nla_tracks
                if nla_strip in track.strips.values()  # type: ignore
            )
            try:
                nla_track = next(nla_tracks)
            except StopIteration:
                self.report(
                    {_WMReport.WARNING},
                    f'Cannot find NLA track for strip "{nla_strip.name}"',
                )
                continue
            finally:
                del nla_tracks
            if nla_track.lock:
                self.report(
                    {_WMReport.WARNING},
                    f'NLA track "{nla_track.name}" for strip "{nla_strip.name}" is locked',
                )
                continue
            index = nla_track.strips.find(nla_strip.name)
            if index == -1:
                self.report(
                    {_WMReport.WARNING},
                    f'Cannot find NLA strip "{nla_strip.name}" in track "{nla_track.name}"',
                )
                continue

            length = nla_strip.frame_end - nla_strip.frame_start
            start_min = (
                int(nla_track.strips[index - 1].frame_end)
                if index >= 1
                else context.scene.frame_start
            )
            start_max = int(
                (
                    nla_track.strips[index + 1].frame_start
                    if (index + 1) < len(nla_track.strips)
                    else context.scene.frame_end
                )
                - length
            )
            if start_min > start_max:
                self.report(
                    {_WMReport.WARNING},
                    f'Cannot randomize NLA strip "{nla_track.name}" [{start_min}, {start_max}]',
                )
                continue
            nla_strip.frame_start_ui = _randint(start_min, start_max)
            self.report({_WMReport.INFO}, f'Randomized NLA strip "{nla_strip.name}"')
            processed += 1
        self.report({_WMReport.INFO}, f"Randomized {processed} NLA strip(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class SynchronizeSteppedInterpolationFModifier(_Op):
    """Synchronize stepped interpolation F-modifier(s) for selected NLA strip(s)"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "nla.sychronize_stepped_interpolation_fmodifier"
    bl_label: _ClassVar = "Synchronize Stepped Interpolation F-Modifier(s)"
    bl_options: _ClassVar = {_OpTypeFlag.REGISTER, _OpTypeFlag.UNDO}
    bl_property: _ClassVar = "select"

    step_size: _Annotated[float, _FloatProp]
    offset: _Annotated[float, _FloatProp]
    select_items: _ClassVar = {
        "USE_EXISTING": _enum_prop_item(
            "USE_EXISTING",
            "Use Existing",
            "Use the existing F-modifier at the specified index",
            number=0,
        ),
        "ADD_IF_NOT_EXIST": _enum_prop_item(
            "ADD_IF_NOT_EXIST",
            "Add If Not Exist",
            "Add a F-modifier if not exist, otherwise use the existing one at the specified index",
            number=1,
        ),
        "ALWAYS_ADD": _enum_prop_item(
            "ALWAYS_ADD", "Always Add", "Always add a F-modifier", number=2
        ),
    }
    select: _Annotated[str, _EnumProp]
    existing_index: _Annotated[int, _IntProp]

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return bool(context.selected_nla_strips)

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        processed = 0
        strips = tuple(context.selected_nla_strips)
        _NLA_SELECT_ALL(action="DESELECT")
        for strip in strips:
            try:
                if self.select == "ALWAYS_ADD":
                    raise IndexError()
                mod = tuple(
                    mod for mod in strip.modifiers if mod.type == _FModType.STEPPED
                )[self.existing_index]
            except IndexError:
                if self.select == "USE_EXISTING":
                    continue
                strip.select = True
                _NLA_FMODIFIER_ADD(type=_FModType.STEPPED, only_active=False)
                strip.select = False
                mod = next(
                    mod
                    for mod in reversed(strip.modifiers)
                    if mod.type == _FModType.STEPPED
                )
            mod = _cast(_FModStepped, mod)
            mod.frame_step = self.step_size
            mod.frame_offset = -strip.frame_start + self.offset
            processed += 1
        for strip in strips:
            strip.select = True
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}

    def invoke(
        self,
        context: _Ctx,
        event: _Evt,
    ):
        return context.window_manager.invoke_props_dialog(self)


SynchronizeSteppedInterpolationFModifier.__annotations__.update(
    {
        "step_size": _FloatProp(
            name="Step Size",
            description="Number of frames to hold per step",
            default=2,
            options={_PropFlag.SKIP_SAVE},
        ),
        "offset": _FloatProp(
            name="Offset",
            description="Reference number of frames before frames get held",
            default=0,
            options={_PropFlag.SKIP_SAVE},
        ),
        "select": _EnumProp(
            name="Select",
            items=SynchronizeSteppedInterpolationFModifier.select_items.values(),  # type: ignore
            description="Selection of F-modifier(s) to apply the operation on",
            default="USE_EXISTING",
            options={_PropFlag.SKIP_SAVE},
        ),
        "existing_index": _IntProp(
            name="Existing Index",
            description="Index of existing F-modifier(s)",
            default=-1,
            options={_PropFlag.SKIP_SAVE},
        ),
    }
)


@_draw_func_class
@_int_op(uuid="f11f0af4-bbec-44d0-9ceb-4386f07ef2c6")
class DrawFunc(_Op):
    __slots__: _ClassVar = ()

    @classmethod
    def NLA_MT_edit_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.operator(CopySelectedNLATrack.bl_idname)
        self.layout.operator(RandomizeSelectedNLAStrip.bl_idname)
        self.layout.operator(SynchronizeSteppedInterpolationFModifier.bl_idname)


register, unregister = _reg_cls_fac(
    (
        CopySelectedNLATrack,
        RandomizeSelectedNLAStrip,
        SynchronizeSteppedInterpolationFModifier,
        DrawFunc,
    )
)
