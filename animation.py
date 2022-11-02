# animation

import random as _random
import bpy as _bpy
import texts.common as _common


def _copy_nla_strip(to_strip, from_strip):
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


def _copy_nla_track(to_track, from_track):
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
    bl_idname = 'nla.copy_selected_track'
    bl_label = 'Copy Selected NLA Track(s)'
    bl_options = frozenset({'REGISTER', 'UNDO'})

    @classmethod
    def poll(cls, context):
        nla_track = context.active_nla_track
        if nla_track is None:
            return False
        return any(obj is not nla_track.id_data for obj in context.selected_objects)

    def execute(self, context):
        processed = 0
        from_track = context.active_nla_track
        for obj in (obj for obj in context.selected_objects
                    if obj is not from_track.id_data):
            _common.utils.ensure_animation_data(obj)
            to_track = obj.animation_data.nla_tracks.new()
            _copy_nla_track(to_track, from_track)

            current_frame = context.scene.frame_current
            lock = to_track.lock
            try:
                to_track.lock = False

                transitions = []
                for index, strip in enumerate(from_track.strips):
                    if strip.type == 'TRANSITION':
                        transitions.append(index)
                    elif strip.type == 'CLIP':
                        _copy_nla_strip(to_track.strips.new(
                            strip.name,
                            int(strip.frame_start),
                            strip.action
                        ), strip)
                    elif strip.type == 'SOUND':
                        context.scene.frame_current = int(strip.frame_start)
                        _bpy.ops.nla.soundclip_add()
                        new_strip = to_track.strips[-1]
                        _copy_nla_strip(new_strip, strip)
                    else:
                        self.report({'WARNING'},
                                    f'Unsupported NLA strip "{strip.name}"')
                for transition in transitions:
                    trans_from = to_track.strips[index - 1]
                    trans_to = to_track.strips[index]
                    _bpy.ops.nla.select_all('DESELECT')
                    trans_from.select = trans_to.select = True
                    _bpy.ops.nla.transition_add()
                    trans_from.select = trans_to.select = False
            finally:
                to_track.lock = lock
                context.scene.frame_current = current_frame

            processed += 1
            self.report({'INFO'},
                        f'Copied to object "{obj.name_full}"')
        self.report({'INFO'}, f'Copied to {processed} object(s)')
        return {'FINISHED'} if processed > 0 else {'CANCELLED'}


class RandomizeSelectedNLAStrip(_bpy.types.Operator):
    '''Randomize time of selected NLA strip(s), preserving order'''
    bl_idname = 'nla.randomize_selected_strip'
    bl_label = 'Randomize Selected NLA Strip(s)'
    bl_options = frozenset({'REGISTER', 'UNDO'})

    @classmethod
    def poll(cls, context):
        return context.selected_nla_strips

    def execute(self, context):
        processed = 0

        for nla_strip in context.selected_nla_strips:
            nla_tracks = (track for track
                          in nla_strip.id_data.animation_data.nla_tracks
                          if nla_strip in track.strips.values())
            try:
                nla_track = next(nla_tracks)
            except StopIteration:
                self.report({'WARNING'},
                            f'Cannot find NLA track for strip "{nla_strip.name}"')
                continue
            finally:
                del nla_tracks
            if nla_track.lock:
                self.report({'WARNING'},
                            f'NLA track "{nla_track.name}" for strip "{nla_strip.name}" is locked')
                continue
            index = nla_track.strips.find(nla_strip.name)
            if index == -1:
                self.report({'WARNING'},
                            f'Cannot find NLA strip "{nla_strip.name}" in track "{nla_track.name}"')
                continue

            length = nla_strip.frame_end - nla_strip.frame_start
            start_min = nla_track.strips[index - 1].frame_end\
                if index >= 1 else context.scene.frame_start
            start_max = (nla_track.strips[index + 1].frame_start
                         if (index + 1) < len(nla_track.strips) else context.scene.frame_end)\
                - length
            if start_min > start_max:
                self.report({'WARNING'},
                            f'Cannot randomize NLA strip "{nla_track.name}" [{start_min}, {start_max}]')
                continue
            nla_strip.frame_start_ui = _random.randint(start_min, start_max)
            self.report({'INFO'},
                        f'Randomized NLA strip "{nla_strip.name}"')
            processed += 1
        self.report({'INFO'},
                    f'Randomized {processed} NLA strip(s)')
        return {'FINISHED'} if processed > 0 else {'CANCELLED'}


@_common.types.draw_func_class
@_common.types.internal_operator(uuid='f11f0af4-bbec-44d0-9ceb-4386f07ef2c6')
class DrawFunc(_bpy.types.Operator):
    @classmethod
    def NLA_MT_edit_draw_func(cls, self, context):
        self.layout.separator()
        self.layout.operator(CopySelectedNLATrack.bl_idname)
        self.layout.operator(RandomizeSelectedNLAStrip.bl_idname)


register, unregister = _common.utils.register_classes_factory((
    CopySelectedNLATrack,
    RandomizeSelectedNLAStrip,
    DrawFunc,
))

if __name__ == '__main__':
    _common.utils.main(register=register, unregister=unregister)
