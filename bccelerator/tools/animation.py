# animation

import bpy as _bpy
import random as _random
import typing as _typing

from .. import util as _util
from ..util import enums as _util_enums
from ..util import types as _util_types
from ..util import utils as _util_utils


def _copy_nla_strip(to_strip: _bpy.types.NlaStrip, from_strip: _bpy.types.NlaStrip) -> None:
    attr: str
    for attr in (
            'action',
            'action_frame_end',
            'action_frame_start',
            # 'active',
            'blend_in',
            'blend_out',
            'blend_type',
            'extrapolation',
            # 'fcurves',
            'frame_end',
            # 'frame_end_ui',
            'frame_start',
            # 'frame_start_ui',
            'influence',
            # 'modifiers',
            'mute',
            'name',
            'repeat',
            'scale',
            # 'select',
            'strip_time',
            # 'strips',
            # 'type',
            'use_animated_influence',
            'use_animated_time',
            'use_animated_time_cyclic',
            'use_auto_blend',
            'use_reverse',
            'use_sync_length',
    ):
        setattr(to_strip, attr, getattr(from_strip, attr))


def _copy_nla_track(to_track: _bpy.types.NlaTrack, from_track: _bpy.types.NlaTrack) -> None:
    attr: str
    for attr in (
            # 'active',
            # 'is_override_data',
            # 'is_solo',
            'lock',
            'mute',
            'name',
            # 'select',
            # 'strips',
    ):
        setattr(to_track, attr, getattr(from_track, attr))


class CopySelectedNLATrack(_bpy.types.Operator):
    '''Copy selected NLA track(s) to selected object(s)'''
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'nla.copy_selected_track'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Copy Selected NLA Track(s)'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({
            _util_enums.OperatorTypeFlag.REGISTER, _util_enums.OperatorTypeFlag.UNDO, })
    )

    @classmethod
    def poll(  # type: ignore
            cls: type[_typing.Self], context: _bpy.types.Context
    ) -> bool:
        nla_track: _bpy.types.NlaTrack | None = context.active_nla_track
        if nla_track is None:
            return False
        return any(obj is not nla_track.id_data for obj in context.selected_objects)

    def execute(  # type: ignore
        self: _typing.Self, context: _bpy.types.Context
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed: int = 0
        from_track: _bpy.types.NlaTrack = context.active_nla_track
        obj: _bpy.types.Object
        for obj in context.selected_objects:
            if obj is not from_track.id_data:
                to_track: _bpy.types.NlaTrack = _util.intersection2(
                    _util_utils.ensure_animation_data(obj).nla_tracks)[0].new()
                _copy_nla_track(to_track, from_track)

                current_frame: int = context.scene.frame_current
                lock: bool = to_track.lock
                try:
                    to_track.lock = False

                    transitions: _typing.MutableSequence[int] = []
                    index: int
                    strip: _bpy.types.NlaStrip
                    for index, strip in enumerate(_util.intersection2(from_track.strips)[1]):
                        if strip.type == _util_enums.NLAStrip.Type.TRANSITION:
                            transitions.append(index)
                        elif strip.type == _util_enums.NLAStrip.Type.CLIP:
                            _copy_nla_strip(_util.intersection2(to_track.strips)[0].new(
                                strip.name,
                                int(strip.frame_start),
                                strip.action
                            ), strip)
                        elif strip.type == _util_enums.NLAStrip.Type.SOUND:
                            context.scene.frame_current = int(
                                strip.frame_start)
                            (_bpy.ops.nla.soundclip_add  # type: ignore
                             )()
                            new_strip: _bpy.types.NlaStrip = to_track.strips[-1]
                            _copy_nla_strip(new_strip, strip)
                        else:
                            self.report({str(_util_enums.WMReport.WARNING)},
                                        f'Unsupported NLA strip "{strip.name}"')
                    transition: int
                    for transition in transitions:
                        trans_from = to_track.strips[transition - 1]
                        trans_to = to_track.strips[transition]
                        (_bpy.ops.nla.select_all  # type: ignore
                         )(action='DESELECT')
                        trans_from.select = trans_to.select = True
                        (_bpy.ops.nla.transition_add  # type: ignore
                         )()
                        trans_from.select = trans_to.select = False
                finally:
                    to_track.lock = lock
                    context.scene.frame_current = current_frame

                processed += 1
                self.report({str(_util_enums.WMReport.INFO)},
                            f'Copied to object "{obj.name_full}"')
        self.report({str(_util_enums.WMReport.INFO)},
                    f'Copied to {processed} object(s)')
        return {_util_enums.OperatorReturn.FINISHED} if processed > 0 else {_util_enums.OperatorReturn.CANCELLED}


class RandomizeSelectedNLAStrip(_bpy.types.Operator):
    '''Randomize time of selected NLA strip(s), preserving order'''
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'nla.randomize_selected_strip'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Randomize Selected NLA Strip(s)'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({
            _util_enums.OperatorTypeFlag.REGISTER, _util_enums.OperatorTypeFlag.UNDO, })
    )

    @classmethod
    def poll(  # type: ignore
            cls: type[_typing.Self], context: _bpy.types.Context
    ) -> bool:
        return bool(context.selected_nla_strips)

    def execute(  # type: ignore
        self: _typing.Self, context: _bpy.types.Context
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed: int = 0
        nla_strip: _bpy.types.NlaStrip
        for nla_strip in context.selected_nla_strips:
            nla_tracks: _typing.Iterator[_bpy.types.NlaTrack] = (track for track
                                                                 in _util.intersection2(_util_utils.ensure_animation_data(_typing.cast(_bpy.types.ID, nla_strip.id_data)).nla_tracks)[1]
                                                                 if nla_strip in (_util.intersection2(track.strips)[1]
                                                                                  .values  # type: ignore
                                                                                  )())
            try:
                nla_track: _bpy.types.NlaTrack = next(nla_tracks)
            except StopIteration:
                self.report({str(_util_enums.WMReport.WARNING)},
                            f'Cannot find NLA track for strip "{nla_strip.name}"')
                continue
            finally:
                del nla_tracks
            if nla_track.lock:
                self.report({str(_util_enums.WMReport.WARNING)},
                            f'NLA track "{nla_track.name}" for strip "{nla_strip.name}" is locked')
                continue
            index: int = _util.intersection2(nla_track.strips)[
                1].find(nla_strip.name)
            if index == -1:
                self.report({str(_util_enums.WMReport.WARNING)},
                            f'Cannot find NLA strip "{nla_strip.name}" in track "{nla_track.name}"')
                continue

            length: float = nla_strip.frame_end - nla_strip.frame_start
            start_min: int = int(
                nla_track.strips[index - 1].frame_end) if index >= 1 else context.scene.frame_start
            start_max: int = int((nla_track.strips[index + 1].frame_start
                                  if (index + 1) < len(_typing.cast(_typing.Collection[_bpy.types.NlaStrip], nla_track.strips))
                                  else context.scene.frame_end)
                                 - length)
            if start_min > start_max:
                self.report({str(_util_enums.WMReport.WARNING)},
                            f'Cannot randomize NLA strip "{nla_track.name}" [{start_min}, {start_max}]')
                continue
            nla_strip.frame_start_ui = _random.randint(start_min, start_max)
            self.report({str(_util_enums.WMReport.INFO)},
                        f'Randomized NLA strip "{nla_strip.name}"')
            processed += 1
        self.report({str(_util_enums.WMReport.INFO)},
                    f'Randomized {processed} NLA strip(s)')
        return {_util_enums.OperatorReturn.FINISHED} if processed > 0 else {_util_enums.OperatorReturn.CANCELLED}


@_util_types.draw_func_class
@_util_types.internal_operator(uuid='f11f0af4-bbec-44d0-9ceb-4386f07ef2c6')
class DrawFunc(_bpy.types.Operator):
    @classmethod
    def NLA_MT_edit_draw_func(cls: type[_typing.Self], self: _typing.Any, context: _bpy.types.Context) -> None:
        layout: _bpy.types.UILayout = self.layout
        layout.separator()
        layout.operator(CopySelectedNLATrack.bl_idname)
        layout.operator(RandomizeSelectedNLAStrip.bl_idname)


register: _typing.Callable[[], None]
unregister: _typing.Callable[[], None]
register, unregister = _util_utils.register_classes_factory((
    CopySelectedNLATrack,
    RandomizeSelectedNLAStrip,
    DrawFunc,
))
