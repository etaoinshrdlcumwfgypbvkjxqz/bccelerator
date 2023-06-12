# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy.types import (
    Context as _Ctx,
    ID as _ID,
    Library as _Lib,
    Operator as _Op,
)
from typing import (
    Any as _Any,
    Callable as _Callable,
    Collection as _Collect,
    ClassVar as _ClassVar,
    cast as _cast,
)

from ..patches import contains as _contains, getitem as _getitem
from ..utils import copy_attrs as _copy_attrs
from ..utils.data import all as _all
from ..utils.enums import (
    OperatorReturn as _OpReturn,
    OperatorTypeFlag as _OpTypeFlag,
    SpaceType as _SpaceType,
    WMReport as _WMReport,
)
from ..utils.types import (
    Drawer as _Drawer,
    draw_func_class as _draw_func_class,
    internal_operator as _int_op,
)
from ..utils.utils import (
    register_classes_factory as _reg_cls_fac,
)


class RemapUserToLibraryByName(_Op):
    """Remap selected local data-block(s) to library data-block(s) by name"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "object.remap_user_to_library_by_name"
    bl_label: _ClassVar = "Remap User(s) to Library Data-Block(s) by Name"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return (
            context.space_data
            and context.space_data.type == _SpaceType.OUTLINER
            and any(not id.library for id in context.selected_ids)
        )

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        processed = 0
        local_users = {
            (type(id), id.name): id for id in context.selected_ids if not id.library
        }
        for lib_user, local_user in (
            (user, local_users[type(user), user.name])
            for lib in context.blend_data.libraries
            for user in _cast(_Collect[_ID], lib.users_id)
            if (type(user), user.name) in local_users
        ):
            local_user.user_remap(lib_user)
            processed += 1
            self.report(
                {_WMReport.INFO},
                f'Remapped "{local_user.name_full}" to "{lib_user.name_full}"',
            )
        self.report({_WMReport.INFO}, f"Remapped {processed} data-block(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class RemapUserToLocalByName(_Op):
    """Remap selected library data-block(s) to local data-block(s) by name"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "object.remap_user_to_local_by_name"
    bl_label: _ClassVar = "Remap User(s) to Local Data-Block(s) by Name"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return (
            context.space_data
            and context.space_data.type == _SpaceType.OUTLINER
            and any(id.library for id in context.selected_ids)
        )

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        processed = 0
        all_data = _all(context)
        for lib_user, local_user in (
            (id, _getitem(all_data[type(id)], (id.name, None)))
            for id in context.selected_ids
            if id.library and _contains(all_data[type(id)], (id.name, None))
        ):
            lib_user.user_remap(local_user)
            processed += 1
            self.report(
                {_WMReport.INFO},
                f'Remapped "{lib_user.name_full}" to "{local_user.name_full}"',
            )
        self.report({_WMReport.INFO}, f"Remapped {processed} data-block(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class LocalizeLibrary(_Op):
    """Make all data-blocks of selected library(s) local"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "outliner.localize_library"
    bl_label: _ClassVar = "Localize Library"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return (
            context.space_data
            and context.space_data.type == _SpaceType.OUTLINER
            and any(isinstance(id, _Lib) for id in context.selected_ids)
        )

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        users = tuple(
            user
            for lib in context.selected_ids
            if isinstance(lib, _Lib)
            for user in _cast(_Collect[_ID], lib.users_id)
        )
        to_be_processed = len(users)
        while users:
            retry_users = list[_ID]()
            for user in (user.make_local() for user in users):
                if not user.library:
                    self.report({_WMReport.INFO}, f'Made "{user.name_full}" local')
                else:
                    retry_users.append(user)
            if len(retry_users) == len(users):
                for user in users:
                    self.report(
                        {_WMReport.WARNING},
                        f'Cannot make "{user.name_full}" local',
                    )
                self.report(
                    {_WMReport.WARNING},
                    f'Cannot make "{len(users)}" data-block(s) local',
                )
                break
            users = retry_users
        processed = to_be_processed - len(users)
        self.report({_WMReport.INFO}, f"Made {processed} data-block(s) local")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class CleanUpLibraryWeakReference(_Op):
    """Clean up unused weak reference(s) to external library(s)"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "wm.clean_up_library_weak_reference"
    bl_label: _ClassVar = "Clean Up Library Weak References"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    def execute(
        self,
        context: _Ctx,
    ) -> set[str]:
        data = tuple(
            datum
            for data in _all(context).values()
            for datum in data
            if datum.library_weak_reference and not datum.library
        )
        for datum in data:
            new_datum = datum.copy()
            asset_data = datum.asset_data
            if asset_data:
                new_datum.asset_mark()
                new_asset_data = new_datum.asset_data
                _copy_attrs(
                    new_asset_data,
                    (
                        "active_tag",
                        "author",
                        "catalog_id",
                        "description",
                    ),
                    asset_data,
                )
                for tag in asset_data.tags:
                    new_asset_data.tags.new(tag.name)
            datum.user_remap(new_datum)
            datum.asset_clear()
            new_datum.name = datum.name
            self.report(
                {_WMReport.INFO},
                f'Removed library weak reference of "{datum.name}": "{datum.library_weak_reference.filepath}"',
            )
        processed = len(data)
        self.report(
            {_WMReport.INFO},
            f"Removed {processed} library weak reference(s)",
        )
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


@_draw_func_class
@_int_op(uuid="2947869a-43a8-4f91-bb19-20ffca18edce")
class DrawFunc(_Op):
    __slots__: _ClassVar = ()

    @classmethod
    def OUTLINER_MT_context_menu_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        lambdas = list[_Callable[[], _Any | None]]()
        if RemapUserToLibraryByName.poll(context):
            lambdas.append(
                lambda: self.layout.operator(RemapUserToLibraryByName.bl_idname)
            )
        if RemapUserToLocalByName.poll(context):
            lambdas.append(
                lambda: self.layout.operator(RemapUserToLocalByName.bl_idname)
            )
        if LocalizeLibrary.poll(context):
            lambdas.append(lambda: self.layout.operator(LocalizeLibrary.bl_idname))
        if lambdas:
            self.layout.separator()
            lamb: _Callable[[], _Any | None]
            for lamb in lambdas:
                lamb()

    @classmethod
    def TOPBAR_MT_file_cleanup_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.operator(
            CleanUpLibraryWeakReference.bl_idname, text="Library Weak References"
        )

    @classmethod
    def OUTLINER_MT_collection_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        cls.OUTLINER_MT_context_menu_draw_func(self, context)

    @classmethod
    def OUTLINER_MT_object_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        cls.OUTLINER_MT_context_menu_draw_func(self, context)


register, unregister = _reg_cls_fac(
    (
        RemapUserToLibraryByName,
        RemapUserToLocalByName,
        LocalizeLibrary,
        CleanUpLibraryWeakReference,
        DrawFunc,
    )
)
